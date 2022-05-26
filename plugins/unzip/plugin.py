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

        self.run_image(submission.submission_dir, file_obj)
        self.wait_and_stop()
        
        tmp_dir = self.extract(submission, file_obj, "/tmp/out")
        out_dir = os.path.join(tmp_dir, "out")
        items = os.listdir(out_dir)
        if len(items) > 1:
            file_obj.is_unpacked_archive()

        uuid_list = []
        for item in items:
            shutil.move(os.path.join(out_dir, item), submission.submission_dir)
            new_file = submission.add_file(item)
            uuid_list.append(new_file.uuid)

        self.remove_tmp_dirs()

        self.remove_container()

        return uuid_list





    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = UnzipPlugin