"""
Plugins are the core of the Kogia framework.
"""
import os
import sys
import docker
import random 
import string
import time
import tarfile
import tempfile
import shutil
import json
import shlex
import uuid

from typing import Union

import requests

from .submission import SubmissionFile

from .job import Job

class PluginBase():

    AUTHOR = ""

    def __init__(self, plugin_manager):
        self.pm = plugin_manager
        self._enabled = True
        self._container = False
        self.config = {}
        self._display = {}
        self._options = []

        config_path = os.path.join(self.get_plugin_dir(), "plugin.json")
        if os.path.exists(config_path):
            config_file = open(config_path, "r")
            config_data = config_file.read()
            self.config = json.loads(config_data)
            if "enabled" in self.config:
                self._enabled = self.config['enabled']
                del self.config['enabled']
            config_file.close()

        display_path = os.path.join(self.get_plugin_dir(), "display.json")
        if os.path.exists(display_path):
            display_file = open(display_path, "r")
            display_data = display_file.read()
            self._display = json.loads(display_data)
            display_file.close()

        options_path = os.path.join(self.get_plugin_dir(), "options.json")
        if os.path.exists(options_path):
            options_file = open(options_path, "r")
            options_data = options_file.read()
            self._options= json.loads(options_data)
            options_file.close()
            
        # print(self.config)

    @property
    def has_container(self):
        return self._container

    @classmethod
    def classname(cls):
        return cls.__name__

    @property
    def name(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "name": str(self.__class__.__name__),
            "config": self.config,
            "type": self.PLUGIN_TYPE,
            "author": self.AUTHOR,
            "display": self._display,
            "options": self._options,
            "docs": self.__doc__
        }

    @property
    def enabled(self):
        return self._enabled
        
    def get_plugin_dir(self):
        return os.path.dirname(sys.modules[self.__class__.__module__].__file__)

    def operates_on(self, file_obj, is_primary):
        operates = False
        found = False
        if hasattr(self, 'MIME_TYPES'):
            found = True
            if file_obj.mime_type in self.MIME_TYPES:
                operates = True

        if hasattr(self, 'EXTENSIONS'):
            found = True
            if file_obj.extension in self.EXTENSIONS:
                operates = True

        if hasattr(self, 'PRIMARY_ONLY'):
            found = True
            operates = self.PRIMARY_ONLY and is_primary
                
        if found:
            return operates
        else:
            return True
        
    def export(self, job_obj, export_file):
        """
        Any plugin with type 'export' must implement the export function. 

        Two objects are passed:
          * job_obj: Job object for the corresponding job
          * export_file: ExportFile for the new export

        export_file simplifies data access to data needed for export.
        """
        raise NotImplementedError

class HTTPPluginBase(PluginBase):

    def __init__(self, plugin_manager):
        super().__init__(plugin_manager)
        self._remote_addr = ""
        self._ssl = True
        self._verify = True
        self._token = ""


    def configure(self, remote_addr, ssl=True, verify=True, token=None):
        self._remote_addr = remote_addr
        self._ssl = ssl
        self._verify = verify
        self._token = token
    
    @property
    def protocol(self):
        if self._ssl:
            return "https://"
        else:
            return "http://"
    
    @property
    def headers(self):
        ret_headers = {}
        if self._token is not None:
            key_name = "Token"
            value = ""
            if isinstance(self._token, dict):
                key_name = list(self._token.keys())[0]
                value = self._token[key_name]
            else:
                value = self._token
            
            ret_headers[key_name] = value
        return ret_headers
            

    def get(self, path : str):
        if not path.startswith("/"):
            path = "/" + path
        return requests.get(f"{self.protocol}{self._remote_addr}{path}", headers=self.headers, verify=self._verify)
    
    def post(self, path : str, data=None, files=None):
        if not path.startswith("/"):
            path = "/" + path

        post_data = {}
        post_files = {}


        return requests.post(f"{self.protocol}{self._remote_addr}{path}", 
                             headers=self.headers, 
                             verify=self._verify,
                             files=files,
                             data=data
                            )

class DockerPluginBase(PluginBase):
    
    def __init__(self, name, plugin_manager):
        super().__init__(plugin_manager)
        self.docker_vars = {}
        self._network = False
        self._name = name
        self._running_name = ""
        self._tmp_dirs = []  
        self._container = True 

    @property
    def image_name(self):
        return self._name
    
    def docker_image_exists(self):
        try:
            self.pm.docker.images.get(self._name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def enable_network(self):
        self._network = True

    def disable_network(self):
        self._network = False

    def docker_build(self, nocache=False):
        plugin_dir = self.get_plugin_dir()
        if self.pm.registry is None:
            try:
                self.pm.docker.images.build(path=plugin_dir, tag=self._name, rm=True, nocache=nocache)
            except docker.errors.BuildError as e:
                for line in e.build_log:
                    if 'stream' in line:
                        print(line['stream'].strip())
                raise
        else:
            new_image = self.pm.docker.images.pull(self.pm.registry + "/" + self._name, tag="latest")
            new_image.tag(self._name)

    def docker_rebuild(self):
        self.docker_build(nocache=True)

    def run_image_with_cmd(self, cmd):
        cmd_split = shlex.split(cmd)
        entrypoint = cmd_split[0]
        args = shlex.join(cmd_split[1:])
        return self.pm.docker.containers.run(self._name, args, entrypoint=entrypoint, remove=True, network_mode="none")
    
    def run_image(self, share_dir, job_obj: Job, file_obj: Union[SubmissionFile, str], env_vars=None):
        share_dir = os.path.abspath(share_dir)

        environment = {}

        if env_vars is not None:
            environment = env_vars

        tmp_dir = '/tmp/' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))

        vols = {
            share_dir: {"bind": tmp_dir, 'mode': 'ro'}
        }

        environment['TMPDIR'] = tmp_dir
        if isinstance(file_obj, SubmissionFile):
            environment['SUBMITFILE'] = file_obj.name
        else:
            environment['SUBMITFILE'] = os.path.basename(file_obj)


        self.docker_vars = environment

        if isinstance(file_obj, SubmissionFile):
            self._running_name = self._name + "-" + str(file_obj.uuid)[:18] + "--" + str(job_obj.uuid)[:18]
        else:
            self._running_name = self._name + "-" + str(uuid.uuid4())

        

        container = None
        if self._network:
            job_obj.info_log(str(self.__class__.__name__), "Creating networked container " + self._name)
            container = self.pm.docker.containers.create(self._name, volumes=vols, environment=environment, detach=True, name=self._running_name, network_mode="none")
        else:
            job_obj.info_log(str(self.__class__.__name__), "Creating unnetworked container " + self._name)
            container = self.pm.docker.containers.create(self._name, volumes=vols, environment=environment, detach=True, name=self._running_name)

        self._created = True
        container.start()
        # self._logger.info(f"Started container {self._running_name}")
        print(f"Started container {self._running_name}")
        
        if isinstance(file_obj, SubmissionFile):
            return os.path.join(tmp_dir, file_obj.name)
        else:
            return os.path.join(tmp_dir, os.path.basename(file_obj))
        

    def wait_and_stop(self, timeout=180):
        i = 0
        done = False

        rounds = timeout/5
        
        while i < rounds and not done:
            time.sleep(5)
            container = self.pm.docker.containers.get(self._running_name)
            if container.status != "running":
                done = True
            else:
                i += 1

        if not done:
            print("Stopping container...")
            container = self.pm.docker.containers.get(self._running_name)
            container.stop()

    def remove_container(self, job_obj: Job):
        container = self.pm.docker.containers.get(self._running_name)
        if container.status == "running":
            container.stop()

        job_obj.info_log(str(self.__class__.__name__), container.logs().decode('utf8'))
        job_obj.info_log(str(self.__class__.__name__), "Removing container " + self._name)
        
        if os.getenv("KOGIA_DEBUG") is not None:
            return
        container.remove()

    def remove_tmp_dirs(self):
        if os.getenv("KOGIA_DEBUG") is not None:
            return
        for tmp_dir in self._tmp_dirs:
            shutil.rmtree(tmp_dir)

    def extract(self, cont_path, out_path=None):
        container = self.pm.docker.containers.get(self._running_name)
        strm, stat = container.get_archive(cont_path)
        tar_path = f"/tmp/{self._running_name}-extract-data.tar"
        results = open(tar_path, "wb")
        for chunk in strm:
            results.write(chunk)
        results.close()

        if out_path is None:
            out_path = tempfile.mkdtemp()
            self._tmp_dirs.append(out_path)

        results_tar = tarfile.open(tar_path, "r")
        results_tar.extractall(path=out_path)
        results_tar.close()

        os.remove(tar_path)
        return out_path

    def extract_single_file(self, submission, file_obj, cont_path, bin=False):
        dir_path = os.path.join(submission.submission_dir, file_obj.uuid)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        return self.extract_single_file_to(dir_path, cont_path, bin=bin)

    def extract_single_file_to(self, write_to_dir, cont_path, bin=False):
        filename = os.path.basename(cont_path)

        tmp_dir = tempfile.mkdtemp()

        self.extract(cont_path, out_path=tmp_dir)
        out_file_path = os.path.join(write_to_dir, f"{self._name}-{filename}")
        file_contents = None
        if not bin:
            file_out = open(os.path.join(tmp_dir, filename), 'r')
            file_contents = file_out.read()
            out_file = open(out_file_path, "w")
            out_file.write(file_contents)
            out_file.close()
            file_out.close()
        else:
            file_out = open(os.path.join(tmp_dir, filename), 'rb')
            file_contents = file_out.read()
            out_file = open(out_file_path, "wb")
            out_file.write(file_contents)
            out_file.close()
            file_out.close()

        shutil.rmtree(tmp_dir)
        return file_contents