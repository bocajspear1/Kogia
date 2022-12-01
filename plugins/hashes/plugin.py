from backend.lib.plugin_base import DockerPluginBase
import shutil
import os
import json

class HashesPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []
    DOCKER_IMAGE = 'hashes'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()
        
        hash_output = self.extract_single_file(submission, file_obj, "/tmp/out/hashes.json")
        try:
            hash_obj = json.loads(hash_output)
            file_data = hash_obj['file']

            file_obj.add_metadata("HASH", "MD5:" + file_data['md5'])
            file_obj.add_metadata("HASH", "SHA1:" + file_data['sha1'])
            file_obj.add_metadata("HASH", "SHA256:" + file_data['sha256'])
            file_obj.add_metadata("HASH", "SSDEEP:" + file_data['ssdeep'])
            file_obj.add_metadata("HASH", "IMPHASH:" + file_data['imphash'])
        except json.decoder.JSONDecodeError:
            hash_txt = self.extract_single_file(submission, file_obj, "/tmp/out/hashes.txt")
            hash_split = hash_txt.split("\n")
            file_obj.add_metadata("HASH", "MD5:" + hash_split[0].split(' ')[0])
            file_obj.add_metadata("HASH", "SHA1:" + hash_split[1].split(' ')[0])
            file_obj.add_metadata("HASH", "SHA256:" + hash_split[2].split(' ')[0])

        
        
        

        self.remove_tmp_dirs()
        self.remove_container(job)

        return []

    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()


__PLUGIN__ = HashesPlugin