import importlib
import os

import docker

class PluginManager():

    def __init__(self, plugin_dir="./plugins"):
        self._plugin_dir = plugin_dir
        self.plugins = {}

        self.docker = docker.from_env()

    def load(self):
        module_list = os.listdir(self._plugin_dir)
        for module_dir in module_list:
            dir_list = os.listdir(os.path.join(self._plugin_dir, module_dir))
            if "plugin.py" in dir_list:
                temp = importlib.import_module("plugins." + module_dir + ".plugin")
                shortname = temp.__PLUGIN__.__name__
                self.plugins[shortname] = temp.__PLUGIN__
                temp = self.plugins[shortname](self)
                temp.check()

        # print(self.plugins)

    def get_plugin_list(self, type_string):
        return_list = []
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if plugin.PLUGIN_TYPE == type_string:
                return_list.append(plugin(self))
        return return_list

    def get_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            return self.plugins[plugin_name](self)
        else:
            return None



        # self.logger.info("Local ModuleManager loaded successfully")