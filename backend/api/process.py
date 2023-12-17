from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import Process
from backend.api.helpers import get_pagination

process_endpoints = Blueprint('process_endpoints', __name__)

#
# Process API endpoints
#

@process_endpoints.route('/<uuid>/events', methods=['GET'])
def get_process_events(uuid):
    current_app._db.lock()
    proc = Process(uuid=uuid)
    proc.load(current_app._db)
    if proc.uuid == None:
        current_app._db.unlock()
        return abort(404)
    proc.load_events(current_app._db, as_dict=True)
    
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": proc.events
    })

@process_endpoints.route('/<uuid>/syscalls', methods=['GET'])
def get_process_syscalls(uuid):
    current_app._db.lock()
    proc = Process(uuid=uuid)
    proc.load(current_app._db)
    if proc.uuid == None:
        current_app._db.unlock()
        return abort(404)
    
    skip_int = 0
    limit_int = 20
    try:
        skip_int, limit_int = get_pagination(request)
    except ValueError:
        return abort(400)
    
    proc.load_syscalls(current_app._db, skip=skip_int, limit=limit_int)
    
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": {
            "total": proc.syscall_total,
            "syscalls": proc.syscalls
        }
    })

@process_endpoints.route('/<uuid>/metadata/<metatype>/list', methods=['GET'])
def get_process_metadata_list(uuid, metatype):
    proc = Process(uuid=uuid)
    current_app._db.lock()
    proc.load(current_app._db)
    if proc.uuid == None:
        current_app._db.unlock()
        return abort(404)
    proc.load_metadata(current_app._db)
    current_app._db.unlock()

    return_list = []

    filter = request.args.get('filter')
    metatype = metatype.strip()

    # Will probably want to make more efficient method later

    metadata = proc.metadata 
    for item in metadata:
        if item.key == metatype:
            if filter is not None:
                if filter.lower() not in item.value.lower():
                    continue

            return_list.append(item.value)

    return jsonify({
        "ok": True,
        "result": return_list
    })

@process_endpoints.route('/<uuid>/metadata/list', methods=['GET'])
def get_process_metadata_types(uuid):
    proc = Process(uuid=uuid)
    current_app._db.lock()
    proc.load(current_app._db)
    proc.load_metadata(current_app._db)
    current_app._db.unlock()

    return_map = {}

    metadata = proc.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    return jsonify({
        "ok": True,
        "result": return_map
    })
