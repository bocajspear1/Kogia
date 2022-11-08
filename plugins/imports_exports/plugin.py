from backend.lib.plugin_base import DockerPluginBase
import shutil
import os

class ImportsExportsPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []
    DOCKER_IMAGE = 'imports-exports'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        output = self.extract_single_file(submission, file_obj, "/tmp/out/output.txt")
        # print(output)

        output_split = output.split("\n")
        for line in output_split:
            line_split = line.split(" ")
            line_type = line_split[0]
            if line_type == "IMPORT_LIB":
                file_obj.add_metadata("IMPORT_LIB", line_split[1])
            elif line_type == "IMPORT":
                file_obj.add_metadata("IMPORT", line_split[1])
            elif line_type == "EXPORT":
                file_obj.add_metadata("EXPORT", line_split[1])


        print(output)

        self.remove_tmp_dirs()

        # self.remove_container(job)

        return []

    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = ImportsExportsPlugin