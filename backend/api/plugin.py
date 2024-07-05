from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import Process

plugin_endpoints = Blueprint('plugin_endpoints', __name__)

#
# Plugin API endpoints
#

@plugin_endpoints.route('/list', methods=['GET'])
def get_plugin_list():

    plugin_type = "*"
    if request.args.get('type') is not None:
        plugin_type = request.args.get('type')
    
    current_app._db.lock()
    plugins = current_app._manager.get_plugin_list(plugin_type)
    init_plugins = current_app._manager.initialize_plugins(plugins)
    ret_list = []
    for plugin in init_plugins:
        if not plugin.enabled:
            continue
        ret_list.append(plugin.to_dict())
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": ret_list
    })

@plugin_endpoints.route('/<plugin_name>/info', methods=['GET'])
def get_plugin(plugin_name):
    
    current_app._db.lock()
    plugin = current_app._manager.get_plugin(plugin_name)
    if plugin is None:
        return abort(404)
    init_plugins = current_app._manager.initialize_plugins([plugin])
    plugin = init_plugins[0]

    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": plugin.to_dict()
    })

@plugin_endpoints.route('/<plugin_name>/action/<action>', methods=['GET'])
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

