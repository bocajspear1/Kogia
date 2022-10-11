from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class ClamAVPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'signature'
    INGESTS = []
    DOCKER_IMAGE = 'clamav'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, file_obj)
        self.wait_and_stop()
        
        clamlog = self.extract_single_file(submission, file_obj, "/tmp/out/clamav.log")
        
        print(clamlog)

        self.remove_tmp_dirs()
        self.remove_container()

        return []

    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

    def action_get_version(self):
        version = self.run_image_with_cmd("clamscan -V").decode("utf-8").strip()
        return [{"ClamAV Version": version}]
__PLUGIN__ = ClamAVPlugin