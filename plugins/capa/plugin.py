from backend.lib.plugin_base import DockerPluginBase
import shutil
import os
import json

class CapaPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'signature'
    INGESTS = []
    DOCKER_IMAGE = 'capa'
    AUTHOR = "Jacob Hartman"

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop(timeout=360)
        
        file_out = self.extract_single_file(submission, file_obj, "/tmp/capa-output.json")
        if file_out.strip() != "":
            try:
                capa_json = json.loads(file_out)
                for item in capa_json['rules']:
                    signature_name = item.replace(" ", "_").upper()
                    description = ""
                    if "meta" in capa_json['rules'][item] and 'description' in capa_json['rules'][item]['meta']:
                        description = capa_json['rules'][item]['meta']['description']
                    job.add_signature(self.name, signature_name, file_obj, description)
                job.add_report("Full CAPA JSON Output", file_obj, json.dumps(capa_json, indent=4))
                # print(json.dumps(capa_json, indent=4))
            except json.decoder.JSONDecodeError:
                pass

        # file_out = self.extract_single_file(submission, file_obj, "/tmp/capa-output.txt")
        # job.add_report("Full CAPA Output", file_obj, file_out)

        # print(file_out)
        # 

        # for detect in die_data['detects']:
        #     for value in detect['values']:
        #         if 'type' in value and value['type'].lower() == 'packer':
        #             file_obj.exec_packer = value['name'].lower()

        self.remove_tmp_dirs()
        self.remove_container(job)

        return []


    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()


__PLUGIN__ = CapaPlugin