from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import ExecInstance

execinstance_endpoints = Blueprint('execinstance_endpoints', __name__)


#
# Exec Instance API endpoints
#
@execinstance_endpoints.route('/<uuid>', methods=['GET'])
def get_exec_instance(uuid):
    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)
    exec_instance.load_processes(current_app._db)
    if exec_instance.uuid == None:
        return abort(404)

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": exec_instance.to_dict()
    })


@execinstance_endpoints.route('/<uuid>/metadata/<metatype>/list', methods=['GET'])
def get_execinstance_metadata_list(uuid, metatype):
    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)

    if exec_instance.uuid == None:
        current_app._db.unlock()
        return abort(404)
    exec_instance.load_metadata(current_app._db)
    current_app._db.unlock()

    filter = request.args.get('filter')
    metadata_type = metatype.strip()

    return_list = exec_instance.get_metadata_by_type(metadata_type, data_filter=filter)

    return jsonify({
        "ok": True,
        "result": return_list
    })

@execinstance_endpoints.route('/<uuid>/metadata/list', methods=['GET'])
def get_execinstance_metadata_types(uuid):
    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)

    if exec_instance.uuid == None:
        current_app._db.unlock()
        return abort(404)
    exec_instance.load_metadata(current_app._db)
    current_app._db.unlock()

    return_map = exec_instance.get_metadata_types()

    return jsonify({
        "ok": True,
        "result": return_map
    })
