import argparse
import getpass
import shutil

from colorama import Fore, Back, Style

from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.config import load_config
from backend.auth.db import DBAuth
from backend.auth import ROLES
from backend.lib.plugin_manager import PluginManager


def load_plugin_manager():
    pm = PluginManager()
    pm.load_all(check=False)
    return pm
   

def get_all_plugin_objs(container_only=False):
    pm = load_plugin_manager()
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

def main():
    config = load_config("./config.json")

    db_factory = ArangoConnectionFactory(
        config['kogia']['db_host'], 
        config['kogia']['db_port'], 
        config['kogia']['db_user'], 
        config['kogia']['db_password'],
        config['kogia']['db_name']
    )

    db = db_factory.new()

    parser = argparse.ArgumentParser('Kogia maintenance commands')
    subparsers = parser.add_subparsers(dest="command")

    # adduser
    adduser_parser = subparsers.add_parser("adduser")

    adduser_parser.add_argument('--username', "-u", help="Set username")
    adduser_parser.add_argument('--password', "-p", help="Set password")
    adduser_parser.add_argument('--role', action='append', choices=ROLES)

    # container
    container_parser = subparsers.add_parser("container")

    container_subparser = container_parser.add_subparsers(dest="container_subcmd")
    build_container_parser = container_subparser.add_parser("build")
    check_container_parser = container_subparser.add_parser("check")
    rebuild_container_parser = container_subparser.add_parser("rebuild")

    rebuild_container_parser.add_argument('plugin')

    # container
    dev_parser = subparsers.add_parser("dev")

    dev_subparser = dev_parser.add_subparsers(dest="dev_subcmd")
    clean_dev_parser = dev_subparser.add_parser("dbclean")
    clean_dev_parser.add_argument("--force", action="store_true", help="Force clean")

    args = parser.parse_args()

    if args.command is None:
        print(parser.format_help())
    elif args.command == "container":
        if args.container_subcmd is None:
            print(container_parser.format_help())
        elif args.container_subcmd == 'build':
            plugin_objs = get_all_plugin_objs(container_only=True)
            c = 1
            for plugin_obj in plugin_objs:
                print(f"{Fore.BLUE}{c}/{len(plugin_objs)}{Style.RESET_ALL} Building {plugin_obj.name} container")
                plugin_obj.docker_build()
                c += 1
        elif args.container_subcmd == 'check':
            plugin_objs = get_all_plugin_objs(container_only=True)
            for plugin_obj in plugin_objs:
                
                if plugin_obj.docker_image_exists():
                    print(f"{plugin_obj.name}: {Fore.GREEN}EXISTS{Style.RESET_ALL}")
                else:
                    print(f"{plugin_obj.name}: {Fore.RED}MISSING{Style.RESET_ALL}")
        elif args.container_subcmd == 'rebuild':
            pm = load_plugin_manager()
            plugin_cls = pm.get_plugin(args.plugin)
            if plugin_cls is None:
                print(f"{Fore.RED}Could not find plugin '{args.plugin}'{Style.RESET_ALL}")
                return 1
            plugin_obj = pm.initialize_plugin(plugin_cls)

            print(f"{Fore.YELLOW}Rebuilding {args.plugin}...{Style.RESET_ALL}")
            plugin_obj.docker_rebuild()
            print(f"{Fore.GREEN}Rebuild complete!{Style.RESET_ALL}")


            # plugin_objs = get_all_plugin_objs(container_only=True)
            # for plugin_obj in plugin_objs:
                
            #     if plugin_obj.docker_image_exists():
            #         print(f"{plugin_obj.name}: {Fore.GREEN}EXISTS{Style.RESET_ALL}")
            #     else:
            #         print(f"{plugin_obj.name}: {Fore.RED}MISSING{Style.RESET_ALL}")

    elif args.command == "dev":
        if args.dev_subcmd is None:
            print(dev_parser.format_help())
        elif args.dev_subcmd == 'dbclean':
            if args.force is False:
                print(f"{Fore.RED}WARNING! This removes all data in Kogia! Are you sure?{Style.RESET_ALL}")
                in_val = input("type 'yes'> ")
                if in_val != 'yes':
                    print(f"{Fore.BLUE}Not doing anything, did not get 'yes'.{Style.RESET_ALL}")
                    return
            
            db.truncate_all_collections()
            print(f"{Fore.YELLOW}All data truncated!{Style.RESET_ALL}")


    elif args.command == "adduser":
        username = args.username
        if username is None:
            username = input("Username> ")
        password = args.password
        if password is None:
            password = getpass.getpass("Password> ")
        auth = DBAuth(db)

        if args.role is None or len(args.role) <= 0: 
            print(f"ERROR: Add at least one from from: {ROLES}")
            return 1
        auth.insert_user(username, password, args.role)
        print(f"User {username} added")
        


if __name__ == '__main__':
    main()