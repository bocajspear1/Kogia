from backend.lib.plugin_base import DockerPluginBase


class UnzipPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'unarchive'
    INGESTS = []
    DOCKER_IMAGE = 'unzip'
    MIME_TYPES=['application/zip']

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, submission, file_obj):
        pass

    def check(self):
        print("Loaded unzip plugin in {}".format(self.get_plugin_dir()))
        print(self.docker_image_exists())

__PLUGIN__ = UnzipPlugin