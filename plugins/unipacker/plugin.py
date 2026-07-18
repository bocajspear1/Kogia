from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class UnipackerPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'unpack'
    INGESTS = []
    DOCKER_IMAGE = 'unipacker'

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        tmp_dir = self.extract(f"/tmp/out")
        out_dir = os.path.join(tmp_dir, "out")
        items = os.listdir(out_dir)

        uuid_list = []
        for item in items:
            new_file = submission.generate_file(item)
            new_file.copy_file_from(os.path.join(out_dir, item))
            uuid_list.append(new_file.uuid)
            submission.add_file(new_file)

        self.remove_tmp_dirs()

        self.remove_container(job)

        return uuid_list


    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

    def action_get_version(self):
        version = self.run_image_with_cmd("unipacker --version").decode("utf-8").strip()
        ver_split = version.split(" ", 1)
        return [{"Unipacker Version": ver_split[1]}]

__PLUGIN__ = UnipackerPlugin