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

class PluginBase():
    def __init__(self, plugin_manager):
        self.pm = plugin_manager
        self._enabled = True
        self.config = {}
        config_path = os.path.join(self.get_plugin_dir(), "plugin.json")
        if os.path.exists(config_path):
            config_file = open(config_path, "r")
            config_data = config_file.read()
            self.config = json.loads(config_data)
            if "enabled" in self.config:
                self._enabled = self.config['enabled']
                del self.config['enabled']
        print(self.config)

    @property
    def enabled(self):
        return self._enabled
        
    def get_plugin_dir(self):
        return os.path.dirname(sys.modules[self.__class__.__module__].__file__)

    def operates_on(self, file_obj):
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

        if found:
            return operates
        else:
            return True


class DockerPluginBase(PluginBase):
    
    def __init__(self, name, plugin_manager):
        super().__init__(plugin_manager)
        self.docker_vars = {}
        self._network = False
        self._name = name
        self._running_name = ""
        self._tmp_dirs = []   
    
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
        self.pm.docker.images.build(path=plugin_dir, tag=self._name, rm=True, nocache=nocache)

    def docker_rebuild(self):
        self.docker_build(nocache=True)
    
    def run_image(self, share_dir, file_obj, env_vars=None):
        share_dir = os.path.abspath(share_dir)

        environment = {}

        if env_vars is not None:
            environment = env_vars

        tmp_dir = '/tmp/' + ''.join(random.choice(string.ascii_lowercase) for i in range(8))

        vols = {
            share_dir: {"bind": tmp_dir, 'mode': 'ro'}
        }

        environment['TMPDIR'] = tmp_dir
        environment['SUBMITFILE'] = file_obj.name


        self.docker_vars = environment

        self._running_name = self._name + "-" + file_obj.uuid

        container = None
        if not self._network:
            container = self.pm.docker.containers.create(self._name, volumes=vols, environment=environment, detach=True, name=self._running_name, network_mode="none")
        else:
            container = self.pm.docker.containers.create(self._name, volumes=vols, environment=environment, detach=True, name=self._running_name)

        self._created = True
        container.start()
        # self._logger.info(f"Started container {self._running_name}")
        print(f"Started container {self._running_name}")

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

    def remove_container(self):
        container = self.pm.docker.containers.get(self._running_name)
        if container.status == "running":
            container.stop()
        if os.getenv("KOGIA_DEBUG") is not None:
            return
        container.remove()

    def remove_tmp_dirs(self):
        if os.getenv("KOGIA_DEBUG") is not None:
            return
        for tmp_dir in self._tmp_dirs:
            shutil.rmtree(tmp_dir)

    def extract(self, submission, file_obj, cont_path, out_path=None):
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
        filename = os.path.basename(cont_path)

        dir_path = os.path.join(submission.submission_dir, file_obj.uuid)

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        tmp_dir = tempfile.mkdtemp()

        self.extract(submission, file_obj, cont_path, out_path=tmp_dir)
        out_file_path = os.path.join(dir_path, f"{self._name}-{filename}")
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