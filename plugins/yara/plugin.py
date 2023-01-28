from backend.lib.plugin_base import DockerPluginBase
from backend.lib.data import SIGNATURE_SEVERITY
import shutil
import os
import json
import csv
from io import StringIO

class YARAPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'signature'
    INGESTS = []
    DOCKER_IMAGE = 'yara'

    def __init__(self, plugin_manager, args=None):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)
        self.args = args

    def _parse_yara_output(self, lines, severity, job, file_obj):
        lines = lines.strip()
        line_split = lines.split("\n")
        for line in line_split:
            if line == "":
                continue

            line_split = line.split('[')
            name = "YARA_" + line_split[0].strip()
            metadata_line = line_split[1].split(']')[0]

            print(metadata_line)
            chunks = []
            counter = 0
            last = 0
            in_string = False
            last_char = None
            while counter != len(metadata_line)-1:
                cur_char = metadata_line[counter]
                if cur_char == "," and not in_string:
                    chunks.append(metadata_line[last:counter])
                    last = counter+1
                elif cur_char == '"' and last_char != "\\":
                    if in_string:
                        in_string = False
                    else:
                        in_string = True

                last_char = metadata_line[counter]
                counter += 1
            chunks.append(metadata_line[last:])

            metadata_dict = {}
            for item in chunks:
                item_split = item.split("=")
                print(item_split, item)
                key = item_split[0].lower()
                value = item_split[1]
                if value.startswith('"'):
                    value = value[1:-1]
                metadata_dict[key] = value
        
            description = ""
            if 'id' in metadata_dict:
                del metadata_dict['id']
            if 'fingerprint' in metadata_dict:
                del metadata_dict['fingerprint']

            if 'description' in metadata_dict:
                description = metadata_dict['description']
                del metadata_dict['description']
            if 'author' in metadata_dict:
                description = metadata_dict['author'] + ' - ' + description

            for extra in metadata_dict:
                description += f" {extra}={metadata_dict[extra]}"
            
            print(description)
            job.add_signature(self.name, name, file_obj, description.strip(), severity=severity)

    def run(self, job, file_obj):
        submission = job.submission

        self.run_image(submission.submission_dir, job, file_obj)
        self.wait_and_stop()

        malpedia_rules_output = self.extract_single_file(submission, file_obj, "/tmp/out/yara-malpedia.txt")
        self._parse_yara_output(malpedia_rules_output, SIGNATURE_SEVERITY.MALICIOUS, job, file_obj)
        
        general_rules_out = self.extract_single_file(submission, file_obj, "/tmp/out/yara-out.txt")
        self._parse_yara_output(general_rules_out, SIGNATURE_SEVERITY.SUSPICIOUS, job, file_obj)

        self.remove_tmp_dirs()
        self.remove_container(job)

        return []

    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()


__PLUGIN__ = YARAPlugin