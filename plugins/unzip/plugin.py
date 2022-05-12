from backend.lib.plugin_base import DockerPluginBase


class UnzipPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'unarchive'
    INGESTS = []
    DOCKER_IMAGE = 'unzip'

    def run(self):
        pass

    def check(self):
        print("Loaded unzip plugin in {}".format(self.get_plugin_dir()))
        print(self.docker_image_exists(self.DOCKER_IMAGE))

__PLUGIN__ = UnzipPlugin