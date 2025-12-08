
from fastapi import APIRouter, Request, HTTPException

from backend.lib.data import Process

from .types import PluginDisplay, PluginDisplayList, OptionalStrParam

router = APIRouter(tags=['plugin'])

#
# Plugin API endpoints
#

@router.get('/list')
def get_plugin_list(request : Request, type : OptionalStrParam = None) -> PluginDisplayList:

    plugin_type = "*"
    if type is not None:
        plugin_type = type
    
    request.app._db.lock()
    plugins = request.app._manager.get_plugin_list(plugin_type)
    init_plugins = request.app._manager.initialize_plugins(plugins)
    ret_list = []
    for plugin in init_plugins:
        if not plugin.enabled:
            continue
        display = PluginDisplay(**plugin.to_dict())
        ret_list.append(display)
    request.app._db.unlock()
    return PluginDisplayList(plugins=ret_list)

@router.get('/{plugin_name}/info')
def get_plugin(request : Request, plugin_name : str):
    
    request.app._db.lock()
    plugin = request.app._manager.get_plugin(plugin_name)
    if plugin is None:
        raise HTTPException(404, detail="Invalid plugin name")
    init_plugins = request.app._manager.initialize_plugins([plugin])
    plugin = init_plugins[0]

    request.app._db.unlock()

    plugin_data = PluginDisplay(**plugin.to_dict())

    return plugin_data

@router.get('/{plugin_name}/action/{action}')
def run_plugin_action(plugin_name, action):
    
    current_app._db.lock()
    plugin = current_app._manager.get_plugin(plugin_name)
    if plugin is None:
        return abort(404)
    init_plugins = current_app._manager.initialize_plugins([plugin])
    plugin = init_plugins[0]

    if not hasattr(plugin, action):
        return abort(404)

    action_func = getattr(plugin, action)
    output = action_func()

    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": output
    })

