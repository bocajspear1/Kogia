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

    def run(self, submission, file_obj):
       
        self.run_image(submission.submission_dir, file_obj)

        self.wait_and_stop()

        file_out = self.extract_single_file("/tmp/file-out.txt")
        print("Output:")
        file_out_split = file_out.split("\n")
        file_string = file_out_split[0]
        mime_type = file_out_split[1]

        file_obj.set_mime_type(mime_type)
        file_obj.add_metadata("FILE_STRING", file_string)

        if "PE32" in file_string:
            readpe_out = self.extract_single_file("/tmp/readpe-out.json")
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


            
        elif "ELF" in file_string:
            readelf_data = self.extract_single_file("/tmp/readelf-out.txt")
            readelf_lines = readelf_data.strip().split("\n")

            data = {}

            for line in readelf_lines:
                line_split = line.split(":", 1)
                key = line_split[0].strip().lower()
                value = line_split[1].strip().lower()
                data[key] = value

            print(data)

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

        self.remove_container()

        return []



    def check(self):
        if not self.docker_image_exists():
            self.docker_rebuild()

__PLUGIN__ = SimpleIDPlugin