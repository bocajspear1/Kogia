from backend.lib.plugin_base import DockerPluginBase
import tempfile
import os 

class SimpleIDPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'identify'
    INGESTS = []
    DOCKER_IMAGE = 'simpleid'

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, submission, file_obj):
       
        self.run_image(submission.submission_dir, file_obj)

        self.wait_and_stop()

        file_out = self.extract_single_file("/tmp/file-out.txt")
        print("Output:")
        print(file_out)



    def check(self):
        print("Loaded simpleid plugin in {}".format(self.get_plugin_dir()))
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = SimpleIDPlugin