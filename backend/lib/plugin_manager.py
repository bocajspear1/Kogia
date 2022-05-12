import importlib
import os

import docker

class PluginManager():

    def __init__(self, plugin_dir="./plugins"):
        self._plugin_dir = plugin_dir
        self.plugins = {}
        self.plugins_sorted = {}
        self.docker = docker.from_env()

    def load(self):
        module_list = os.listdir(self._plugin_dir)
        for module_dir in module_list:
            dir_list = os.listdir(os.path.join(self._plugin_dir, module_dir))
            if "plugin.py" in dir_list:
                temp = importlib.import_module("plugins." + module_dir + ".plugin")
                shortname = module_dir
                self.plugins[shortname] = temp.__PLUGIN__(self)
                self.plugins[shortname].check()

                self.plugins_sorted[self.plugins[shortname].PLUGIN_TYPE] = shortname
        print(self.plugins_sorted)


        # self.logger.info("Local ModuleManager loaded successfully")