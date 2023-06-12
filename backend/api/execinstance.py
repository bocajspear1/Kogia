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
