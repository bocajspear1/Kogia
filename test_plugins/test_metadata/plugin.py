from backend.lib.plugin_base import PluginBase
import shutil
import re

DEFAULT_MIN_STR = 5
DEFAULT_MIN_INSERT = 8

class TestMetadataPlugin(PluginBase):
    PLUGIN_TYPE = 'metadata'
    INGESTS = []

    def __init__(self, plugin_manager, args=None):
        super().__init__(plugin_manager)
        self.args = args
        print(args)

    def run(self, job, file_obj):
        
        file_obj.add_metadata("FILE_METADATA1", "DATA1")
        file_obj.add_metadata("FILE_METADATA2", "DATA2")
        return []

    def check(self):
        return True

__PLUGIN__ = TestMetadataPlugin