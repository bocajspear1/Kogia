from backend.lib.plugin_base import DockerPluginBase
import shutil
import re

DEFAULT_MIN_STR = 5
DEFAULT_MIN_INSERT = 8

class StringsPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []
    DOCKER_IMAGE = 'strings'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args
        self._char_count = DEFAULT_MIN_STR
        self._min_insert = DEFAULT_MIN_INSERT

    def _add_strings(self, metadata_name, strings_all, file_obj):
        string_split = strings_all.split("\n")
        for new_string in string_split:
            insert = True
            s_string = new_string.strip()

            if s_string == "":
                insert = False
            # Remove strings with spaces that are actually too short
            if len(s_string) < self._min_insert or len(s_string.replace(" ", "").replace("\t", "")) < self._min_insert:
                insert = False
            # Remove short strings that consist of only numbers and special characters
            if len(s_string) <= DEFAULT_MIN_INSERT and re.match(r'^[!-@\[-`{-~]+$', s_string):
                insert = False

            if insert:
                file_obj.add_metadata(metadata_name, new_string)

    def run(self, job, file_obj):
        submission = job.submission
        
        self._char_count = DEFAULT_MIN_STR
        if self.args is not None and 'minimum' in self.args:
            self._char_count = int(self.args['minimum'])

        self._min_insert = DEFAULT_MIN_INSERT
        if self.args is not None and 'min_insert' in self.args:
            self._min_insert = int(self.args['min_insert'])

        self.run_image(submission.submission_dir, job, file_obj, env_vars={
            "CHAR_COUNT": self._char_count
        })
        self.wait_and_stop()
        
        utf8_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings.txt")
        self._add_strings("STRING", utf8_strings.strip(), file_obj)

        wide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf16.txt")
        self._add_strings("UTF16_STRING", wide_strings.strip(), file_obj)

        verywide_strings = self.extract_single_file(submission, file_obj, "/tmp/out/strings-utf32.txt")
        self._add_strings("UTF32_STRING", verywide_strings.strip(), file_obj)

        all_strings = utf8_strings.strip() + "\n----\n" + wide_strings.strip() + "\n-----\n" + verywide_strings
        
        job.add_report("Full Strings Output", file_obj, all_strings)

        self.remove_tmp_dirs()

        self.remove_container(job)

        return []





    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = StringsPlugin