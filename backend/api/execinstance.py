from base64 import b64encode

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import ExecInstance
from backend.api.helpers import get_pagination, json_resp_ok, json_resp_invalid, json_resp_not_found

execinstance_endpoints = Blueprint('execinstance_endpoints', __name__)


#
# Exec Instance API endpoints
#
@execinstance_endpoints.route('/<uuid>', methods=['GET'])
def get_exec_instance(uuid):
    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)
    
    if exec_instance.uuid == None:
        current_app._db.unlock()
        return json_resp_not_found("Execution instance not found")

    exec_instance.load_processes(current_app._db)
    current_app._db.unlock()

    return json_resp_ok(exec_instance.to_dict())


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

@execinstance_endpoints.route('/<uuid>/netcomm/list', methods=['GET'])
def get_execinstance_netcomm(uuid):

    try:
        limit_int, skip_int = get_pagination(request)
    except ValueError:
        return json_resp_invalid("Parameter 'sort' or 'limit' is invalid")

    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)
    if exec_instance.uuid == None:
        current_app._db.unlock()
        return json_resp_not_found("Execution instance not found")
    
    address_filter = None
    if request.args.get('address') is not None:
        address_filter = request.args.get('address')
    port_filter = None
    if request.args.get('port') is not None:
        try:
            port_filter = int(request.args.get('port'))
        except ValueError:
            return json_resp_invalid("Parameter 'port' is invalid")
    
    exec_instance.load_netcomms(current_app._db, limit=limit_int, skip=skip_int, as_dict=True, port_filter=port_filter, address_filter=address_filter)
    comm_stats = exec_instance.network_comm_statistics
    current_app._db.unlock()

    return json_resp_ok({
        "netcomms": exec_instance.network_comms,
        "total": exec_instance.network_comms_total,
        "statistics": comm_stats
    })

@execinstance_endpoints.route('/<uuid>/thumbnail/<name>', methods=['GET'])
def get_execinstance_thumbnails(uuid, name):

    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)
    if exec_instance.uuid == None:
        current_app._db.unlock()
        return json_resp_not_found("Execution instance not found")
    current_app._db.unlock()

    if name in exec_instance.screenshots:
        thumb_name = f"{name}-t"
        thumb_file = current_app._filestore.open_file(thumb_name)
        encode_image = b64encode(thumb_file.read()).decode()
        current_app._filestore.close_file(name, thumb_file)
        return json_resp_ok({
            "image_data": encode_image,
            "name": thumb_name
        })
    else:
        return json_resp_not_found("Screenshot not found")

@execinstance_endpoints.route('/<uuid>/screenshot/<name>', methods=['GET'])
def get_execinstance_screenshot(uuid, name):

    current_app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(current_app._db)
    if exec_instance.uuid == None:
        current_app._db.unlock()
        return json_resp_not_found("Execution instance not found")
    current_app._db.unlock()

    if name in exec_instance.screenshots:
        screenshot_name = f"{name}-t"
        screenshot_file = current_app._filestore.open_file(name)
        encode_image = b64encode(screenshot_file.read()).decode()
        current_app._filestore.close_file(name, screenshot_file)
        return json_resp_ok({
            "image_data": encode_image,
            "name": screenshot_name
        })
    else:
        return json_resp_not_found("Screenshot not found")

    