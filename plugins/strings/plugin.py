from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class StringsPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []
    DOCKER_IMAGE = 'strings'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def _add_strings(self, metadata_name, strings_all, file_obj):
        string_split = strings_all.split("\n")
        for new_string in string_split:
            if new_string != "":
                print(metadata_name, new_string)
                file_obj.add_metadata(metadata_name, new_string)

    def run(self, job, file_obj):
        submission = job.submission
        
        char_count = 4
        if self.args is not None and 'minimum' in self.args:
            char_count = self.args['minimum']

        self.run_image(submission.submission_dir, job, file_obj, env_vars={
            "CHAR_COUNT": char_count
        })
        self.wait_and_stop()
        
        utf8_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings.txt")
        self._add_strings("STRING", utf8_strings.strip(), file_obj)
        wide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf16.txt")
        self._add_strings("UTF16_STRING", wide_strings.strip(), file_obj)
        verywide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf32.txt")
        self._add_strings("UTF32_STRING", verywide_strings.strip(), file_obj)

        all_strings = utf8_strings.strip() + "\n----\n" + wide_strings.strip() + "\n-----\n" + verywide_strings
        

        self.remove_tmp_dirs()

        self.remove_container(job)

        return []





    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = StringsPlugin