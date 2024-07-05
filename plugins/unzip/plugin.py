from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class UnzipPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'unarchive'
    INGESTS = []
    DOCKER_IMAGE = 'unzip'
    MIME_TYPES=['application/zip']

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        tmp_dir = self.extract("/tmp/out")
        out_dir = os.path.join(tmp_dir, "out")
        items = os.listdir(out_dir)
        if len(items) >= 1:
            file_obj.is_unpacked_archive()

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

__PLUGIN__ = UnzipPlugin