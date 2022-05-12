import os
import sys
import docker

class PluginBase():
    def __init__(self, plugin_manager):
        self.pm = plugin_manager

    def get_plugin_dir(self):
        return os.path.dirname(sys.modules[self.__class__.__module__].__file__)

class DockerPluginBase(PluginBase):
    
    def __init__(self, plugin_manager):
        super().__init__(plugin_manager)
    
    def docker_image_exists(self, name):
        try:
            self.pm.docker.images.get(name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def docker_build(self, name, nocache=False):
        plugin_dir = self.get_plugin_dir()
        self.pm.docker.images.build(path=plugin_dir, tag=name, rm=True, nocache=nocache)

    def docker_rebuild(self, name):
        self.docker_build(name, nocache=True)