from backend.lib.plugin_base import DockerPluginBase
from backend.lib.data import SIGNATURE_SEVERITY

class ClamAVPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'signature'
    INGESTS = []
    DOCKER_IMAGE = 'clamav'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def run(self, job, file_obj):
        submission = job.submission

        test_path = self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        clamlog = self.extract_single_file(submission, file_obj, "/tmp/out/clamav.log")

        job.add_report("ClamAV Scan", file_obj, clamlog)

        clamlog_split = clamlog.split("\n")
        for line in clamlog_split:
            if line.startswith(test_path) and "FOUND" in line:
                line_split = line.split(" ")
                clam_sig = line_split[1]
                print(clam_sig)
                job.add_signature(self.name, clam_sig, file_obj, f"Matched ClamAV signature {clam_sig}", severity=SIGNATURE_SEVERITY.MALICIOUS)

        self.remove_tmp_dirs()
        self.remove_container(job)

        return []

    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

    def action_get_version(self):
        version = self.run_image_with_cmd("clamscan -V").decode("utf-8").strip()
        return [{"ClamAV Version": version}]
__PLUGIN__ = ClamAVPlugin