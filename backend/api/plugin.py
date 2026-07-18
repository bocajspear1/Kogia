
from fastapi import APIRouter, Request, HTTPException

from backend.lib.data import Process

from .types import PluginDisplay, PluginDisplayList, OptionalStrParam, PluginActionResult

router = APIRouter(tags=['plugin'])

#
# Plugin API endpoints
#

@router.get('/list')
def get_plugin_list(req : Request, type : OptionalStrParam = None) -> PluginDisplayList:

    plugin_type = "*"
    if type is not None:
        plugin_type = type
    
    with req.app._db.lock:
        plugins = req.app._manager.get_plugin_list(plugin_type)
        init_plugins = req.app._manager.initialize_plugins(plugins)

    ret_list = []
    for plugin in init_plugins:
        if not plugin.enabled:
            continue
        display = PluginDisplay(**plugin.to_dict())
        ret_list.append(display)
    
    return PluginDisplayList(plugins=ret_list)

@router.get('/{plugin_name}/info')
def get_plugin(req : Request, plugin_name : str) -> PluginDisplay:
    
    with req.app._db.lock:
        plugin = req.app._manager.get_plugin(plugin_name)
        if plugin is None:
            raise HTTPException(404, detail="Invalid plugin name")
        init_plugins = req.app._manager.initialize_plugins([plugin])
        plugin = init_plugins[0]

    plugin_data = PluginDisplay(**plugin.to_dict())

    return plugin_data

@router.get('/{plugin_name}/action/{action}')
def run_plugin_action(req : Request, plugin_name : str, action : str) -> PluginActionResult:
    
    with req.app._db.lock:
        plugin = req.app._manager.get_plugin(plugin_name)
        if plugin is None:
            return HTTPException(404, detail="Invalid plugin name")
        init_plugins = req.app._manager.initialize_plugins([plugin])
        plugin = init_plugins[0]

        if not hasattr(plugin, action):
            return HTTPException(404, detail="Invalid plugin action")

        action_func = getattr(plugin, action)
        output = action_func()
        
        return PluginActionResult(result=output)

