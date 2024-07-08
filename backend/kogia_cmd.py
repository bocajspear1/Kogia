import json
import getpass
import shutil

from colorama import Fore, Back, Style
import click

from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.config import load_config
from backend.auth.db import DBAuth
from backend.auth import ROLES
from backend.lib.plugin_manager import PluginManager
from backend.lib.job import Job
from backend.lib.data import ExecInstance

from backend.lib.helpers import prepare_all


def get_all_plugin_objs(pm, container_only=False):
    plugin_list = pm.get_plugin_list('*')
    inited_plugins = pm.initialize_plugins(plugin_list)

    if container_only:
        out_list = []
        for plugin_obj in inited_plugins:
            if not plugin_obj.has_container:
                continue
            out_list.append(plugin_obj)
        return out_list
    else:
        return inited_plugins

class ContextObj():

    def __init__(self):
        self.config = load_config("./config.json")

        dbf, pm, filestore, workers = prepare_all(self.config, check=False)
        self.db = dbf.new()
        self.pm = pm
        self.filestore = filestore
        self.workers = workers

@click.group()
@click.pass_context
def main_cli(ctx):
    ctx.obj = ContextObj()


#
# run subcommand
#

@main_cli.group('run')
def run_group():
    pass

@run_group.command('web')
@click.option('--port', "-p", help="Port to bind to", default=4000)
@click.option('--addr', "-a", help="Set address to bind to", default="0.0.0.0")
@click.option("--debug", is_flag=True, help="Run in debug mode")
@click.option("--noworkers", is_flag=True, help="Don't run workers too")
@click.option("--waitress", is_flag=True, help="Run with Waitress instead of the default gunicorn")
@click.pass_obj
def web_cmd(ctx, port, addr, debug, noworkers, waitress):
    if debug is True:
        ctx.config['loglevel'] = 'debug'
    try:
        if not waitress:
            from backend.run import run_gunicorn
            run_gunicorn(ctx.config, ctx.workers, addr, int(port))
        else:
            from backend.run import run_waitress
            run_waitress(ctx.config, ctx.workers, addr, int(port))
    except KeyboardInterrupt:
        print("Stopping...")

@run_group.command('workers')
@click.pass_obj
def workers_cmd(ctx):
    try:
        from backend.run import run_workers_only
        run_workers_only(ctx.config, ctx.workers)
    except KeyboardInterrupt:
        print("Stopping...")

#
# dbauth subcommand
#

@main_cli.group('dbauth')
def dbauth_group():
    pass

@dbauth_group.command('adduser')
@click.argument('username')
@click.option('--role', '-r', multiple=True, type=click.Choice(ROLES, case_sensitive=False))
@click.option("--password", help="User password's, be careful using this option")
@click.pass_obj
def adduser_cmd(ctx, username, role, password):
    username = username
    password = password
    if password is None:
        password = getpass.getpass("Password> ")
    auth = DBAuth(ctx.db)

    if role is None or len(role) <= 0: 
        print(f"ERROR: Add at least one from from: {ROLES}")
        return 1
    auth.insert_user(username, password, role)
    print(f"{Fore.GREEN}User {username} added{Style.RESET_ALL}")

#
# container subcommand
#

@main_cli.group('container')
def container_group():
    pass

@container_group.command('build')
@click.pass_obj
def build_cmd(ctx):
    plugin_objs = get_all_plugin_objs(ctx.pm, container_only=True)
    c = 1
    for plugin_obj in plugin_objs:
        print(f"{Fore.BLUE}{c}/{len(plugin_objs)}{Style.RESET_ALL} Building {plugin_obj.name} container")
        plugin_obj.docker_build()
        c += 1

@container_group.command('check')
@click.pass_obj
def check_container_cmd(ctx):
    plugin_objs = get_all_plugin_objs(ctx.pm, container_only=True)
    for plugin_obj in plugin_objs:
        
        if plugin_obj.docker_image_exists():
            print(f"{plugin_obj.name}: {Fore.GREEN}EXISTS{Style.RESET_ALL}")
        else:
            print(f"{plugin_obj.name}: {Fore.RED}MISSING{Style.RESET_ALL}")

@container_group.command('rebuild')
@click.argument('plugin')
@click.pass_obj
def rebuild_container_cmd(ctx, plugin):
    plugin_cls = ctx.pm.get_plugin(plugin)
    if plugin_cls is None:
        print(f"{Fore.RED}Could not find plugin '{plugin}'{Style.RESET_ALL}")
        return 1
    plugin_obj = ctx.pm.initialize_plugin(plugin_cls)

    print(f"{Fore.YELLOW}Rebuilding {plugin}...{Style.RESET_ALL}")
    plugin_obj.docker_rebuild()
    print(f"{Fore.GREEN}Rebuild complete!{Style.RESET_ALL}")


#
# dev subcommand
#

@main_cli.group('dev')
def dev_group():
    pass

@dev_group.command('dbclean')
@click.option("--force", is_flag=True, help="Force clean")
@click.pass_obj
def dbclean_command(ctx, force):
    if force is False:
        print(f"{Fore.RED}WARNING! This removes all data in Kogia! Are you sure?{Style.RESET_ALL}")
        in_val = input("type 'yes'> ")
        if in_val != 'yes':
            print(f"{Fore.BLUE}Not doing anything, did not get 'yes'.{Style.RESET_ALL}")
            return
    
    ctx.db.truncate_all_collections()
    print(f"{Fore.YELLOW}All data truncated!{Style.RESET_ALL}")

@dev_group.command('plugin')
@click.argument('plugin_name')
@click.argument('job_uuid')
@click.pass_obj
def plugin_run_command(ctx, plugin_name, job_uuid):
    plugin_item = ctx.pm.get_plugin(plugin_name)
    if plugin_item is None:
        print(f"{Fore.RED}Plugin {plugin_name} not found{Style.RESET_ALL}")
        return
    plugin_obj = ctx.pm.initialize_plugin(plugin_item)
    
    job_obj = Job(ctx.db, ctx.filestore, job_uuid)
    job_obj.load(ctx.pm)
    job_obj.load_matches()
    print(job_obj.uuid)

    primary_file = job_obj.get_primary_file()
    print(primary_file)
    plugin_obj.run(job_obj, primary_file)

    job_obj.save()

@dev_group.command('insertdata')
@click.argument('parent_uuid')
@click.argument('filename', type=click.Path(exists=True))
@click.option('--dtype',type=click.Choice(['metadata', 'netcomm', 'syscall'], case_sensitive=False))
@click.pass_obj
def plugin_insert_command(ctx, parent_uuid, filename, dtype):


    if dtype in ('metadata', 'netcomm', 'syscall'):
        inst_obj = ExecInstance(uuid=parent_uuid)
        inst_obj.load(ctx.db)
        print(inst_obj)
        with open(filename, "r") as data_file:
            data_dict = json.load(data_file)
            for item in data_dict:
                if dtype == 'netcomm':
                    print("Loading networking comm...")
                    inst_obj.add_network_comm(**item)
            inst_obj.save(ctx.db)
    elif dtype in ('report',):
        job_obj = Job(ctx.db, ctx.filestore, parent_uuid)
        job_obj.load(ctx.pm)

        job_obj.add_report()


if __name__ == '__main__':
    main_cli()
