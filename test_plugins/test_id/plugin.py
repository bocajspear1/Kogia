from backend.lib.plugin_base import PluginBase
from backend.lib.data import SubmissionFile
import tempfile
import os
import json 

class TestIDPlugin(PluginBase):
    PLUGIN_TYPE = 'identify'
    INGESTS = []
    

    def __init__(self, plugin_manager):
        super().__init__(plugin_manager)

    def run(self, job, file_obj : SubmissionFile):
        submission = job.submission

        if file_obj.name.endswith(".elf"):
            file_obj.exec_arch = "amd64"
            file_obj.mime_type = "application/x-elf"
            file_obj.exec_format = "elf"
            file_obj.exec_interpreter = "native"
            file_obj.exec_bits = "64"
            file_obj.exec_type = "executable"
            file_obj.target_os = 'linux'
        elif file_obj.name.endswith(".so"):
            file_obj.exec_arch = "amd64"
            file_obj.mime_type = "application/x-sharedlib"
            file_obj.exec_format = "elf"
            file_obj.exec_interpreter = "native"
            file_obj.exec_bits = "64"
            file_obj.exec_type = "library"
            file_obj.target_os = 'linux'
        elif file_obj.name.endswith(".exe"):
            file_obj.exec_arch = "amd64"
            file_obj.mime_type = "application/vnd.microsoft.portable-executable"
            file_obj.exec_format = "pe"
            file_obj.exec_interpreter = "native"
            file_obj.exec_bits = "64"
            file_obj.exec_type = "executable"
            file_obj.target_os = 'windows'
        elif file_obj.name.endswith(".so"):
            file_obj.exec_arch = "amd64"
            file_obj.mime_type = "application/vnd.microsoft.portable-executable"
            file_obj.exec_format = "pe"
            file_obj.exec_interpreter = "native"
            file_obj.exec_bits = "64"
            file_obj.exec_type = "library"
            file_obj.target_os = 'windows'
        elif file_obj.name.endswith(".pdf"):
            file_obj.mime_type = "application/pdf"
        elif file_obj.name.endswith(".docx"):
            file_obj.mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_obj.name.endswith(".xlsx"):
            file_obj.mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml"

        return []



    def check(self):
        pass

__PLUGIN__ = TestIDPlugin