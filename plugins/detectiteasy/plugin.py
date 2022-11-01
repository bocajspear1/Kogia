from backend.lib.plugin_base import DockerPluginBase
import shutil
import os
import json

class DetectItEasyPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'identify'
    INGESTS = []
    DOCKER_IMAGE = 'detectiteasy'
    AUTHOR = "Jacob Hartman"

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        file_out = self.extract_single_file(submission, file_obj, "/tmp/die-out.json")
        die_data = json.loads(file_out)

        for detect in die_data['detects']:
            for value in detect['values']:
                if 'type' in value and value['type'].lower() == 'packer':
                    file_obj.exec_packer = value['name'].lower()

        self.remove_tmp_dirs()
        self.remove_container(job)

        return []


    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

    def action_get_version(self):
        version = self.run_image_with_cmd("diec -v").decode("utf-8").strip()
        ver_split = version.split(" ", 1)
        return [{"DiE Version": ver_split[1]}]

__PLUGIN__ = DetectItEasyPlugin