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

    def run(self, submission, file_obj):

        self.run_image(submission.submission_dir, file_obj)
        self.wait_and_stop()
        
        tmp_dir = self.extract("/tmp/out")
        out_dir = os.path.join(tmp_dir, "out")
        items = os.listdir(out_dir)
        if len(items) > 1:
            file_obj.is_unpacked_archive()

        for item in items:
            shutil.move(os.path.join(out_dir, item), submission.submission_dir)
            submission.add_file(item)


        self.remove_tmp_dirs()

        self.remove_container()

        return items





    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = UnzipPlugin