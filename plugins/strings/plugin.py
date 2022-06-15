from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class StringsPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []
    DOCKER_IMAGE = 'strings'

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, file_obj)
        self.wait_and_stop()
        
        strings1 = self.extract_single_file(submission, file_obj, "/tmp/out/strings.txt")
        wide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf16.txt")
        verywide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf32.txt")

        all_strings = strings1.strip() + "\n" + wide_strings.strip() + "\n" + verywide_strings
        print(all_strings)

        self.remove_tmp_dirs()

        self.remove_container()

        return []





    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = StringsPlugin