from backend.lib.plugin_base import DockerPluginBase
import tempfile
import os
import json 

class SimpleIDPlugin(DockerPluginBase):
    PLUGIN_TYPE = 'identify'
    INGESTS = []
    DOCKER_IMAGE = 'simpleid'

    def __init__(self, plugin_manager):
        super().__init__(self.DOCKER_IMAGE, plugin_manager)

    def run(self, job, file_obj):
        submission = job.submission
       
        self.run_image(submission.submission_dir, job, file_obj)

        self.wait_and_stop()

        file_out = self.extract_single_file(submission, file_obj, "/tmp/file-out.txt")
        file_out_split = file_out.split("\n")
        file_string = file_out_split[0]
        mime_type = file_out_split[1]

        file_obj.mime_type = mime_type
        file_obj.add_metadata("FILE_STRING", file_string)

        if "PE32" in file_string:
            readpe_out = self.extract_single_file(submission, file_obj, "/tmp/readpe-out.json")
            readpe_data = json.loads(readpe_out)

            machine = readpe_data["COFF/File header"]['Machine']
            machine_split = machine.split(" ", 1)
            if machine_split[1] == "IMAGE_FILE_MACHINE_AMD64":
                file_obj.exec_bits = "64"
                file_obj.exec_arch = 'amd64'
            elif machine_split[1] == "IMAGE_FILE_MACHINE_I386":
                file_obj.exec_bits = "32"
                file_obj.exec_arch = 'i386'
            file_obj.exec_format = "pe"

            characteristics = readpe_data["COFF/File header"]['Characteristics names']
            if "IMAGE_FILE_EXECUTABLE_IMAGE" in characteristics:
                if "IMAGE_FILE_DLL" in characteristics:
                    file_obj.exec_type = "library"
                else:
                    file_obj.exec_type = "executable"

            if "Data directories" in readpe_data:
                found = False
                for item in readpe_data["Data directories"]:
                    if "IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR" in item:
                        file_obj.exec_interpreter = 'dotnet'
                        found = True
                
                if not found:
                    file_obj.exec_interpreter = 'native'
                
            else:
                file_obj.exec_interpreter = 'native'

            file_obj.target_os = 'windows'
            
        elif "ELF" in file_string:
            readelf_data = self.extract_single_file(submission, file_obj, "/tmp/readelf-out.txt")
            readelf_lines = readelf_data.strip().split("\n")

            file_obj.exec_interpreter = 'native'

            data = {}

            for line in readelf_lines:
                line_split = line.split(":", 1)
                if len(line_split) < 2:
                    continue
                key = line_split[0].strip().lower()
                if key.startswith("["):
                    key = key[1:]
                value = line_split[1].strip().lower()
                if value.endswith("]"):
                    value = value[:-1]
                data[key] = value

            if data["class"] == 'elf32':
                file_obj.exec_bits = "32"
                file_obj.exec_format = "elf"
            elif data["class"] == 'elf64':
                file_obj.exec_bits = "64"
                file_obj.exec_format = "elf"

            
            if 'exec' in data['type']:
                file_obj.exec_type = 'executable'
            elif 'dyn' in data['type']:
                file_obj.exec_type = 'library'

            if 'x86-64' in data['machine']:
                file_obj.exec_arch = 'amd64'
            elif 'intel 80386' in data['machine']:
                file_obj.exec_arch = 'i386'
            elif 'mips' in data['machine']:
                if data['class'] == 'elf32':
                    file_obj.exec_arch = 'mips32'
                elif data['class'] == 'elf64':
                    file_obj.exec_arch = 'mips64'
                elif 'little endian' in data['data'] and data['class'] == 'elf32':
                    file_obj.exec_arch = 'mipsel'
            elif 'arm' in data['machine']:
                 file_obj.exec_arch = 'arm32'
            elif 'aarch64' in data['machine']:
                 file_obj.exec_arch = 'aarch64'

            if 'system v' in data['os/abi']:
                file_obj.target_os = "generic-system-v"
            elif 'freebsd' in data['os/abi']:
                file_obj.target_os = "freebsd"
            elif 'openbsd' in data['os/abi']:
                file_obj.target_os = "openbsd"
            elif 'netbsd' in data['os/abi']:
                file_obj.target_os = "netbsd"
            elif 'aix' in data['os/abi']:
                file_obj.target_os = "aix"
            else:
                file_obj.target_os = "unknown"

        self.remove_container(job)

        return []



    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = SimpleIDPlugin