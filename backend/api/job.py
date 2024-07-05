from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.job import Job
from backend.lib.helpers import generate_download_token
from backend.api.helpers import get_pagination, json_resp_failed, json_resp_not_found, json_resp_invalid

job_endpoints = Blueprint('job_endpoints', __name__)

#
# Job API endpoints
#

@job_endpoints.route('/list', methods=['GET'])
def get_job_list():
    current_app._db.lock()

    skip_int = 0
    limit_int = 30
    try:
        limit_int, skip_int = get_pagination(request)
    except ValueError:
        return abort(400)
        
    job_list = []
    total_len = 0
    submission_uuid = request.args.get('submission')
    if submission_uuid is None:
        total_len, job_list = Job.list_dict(current_app._db, skip=skip_int, limit=limit_int)
    else:
        total_len, job_list = Job.list_dict(current_app._db, skip=skip_int, limit=limit_int, submission_uuid=submission_uuid)
        
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": {
            "jobs": job_list,
            "total": total_len
        }
    })

@job_endpoints.route('/<uuid>/info', methods=['GET'])
def get_job_status(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        current_app._db.unlock()
        return abort(404)
    resp = job.to_dict()
    signature_list = job.get_signatures()
    resp['signature_count'] = len(signature_list)
    reports_list = job.get_reports()
    resp['report_count'] = len(reports_list)
    exec_inst_list = job.get_exec_instances()
    resp['exec_inst_count'] = len(exec_inst_list)
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": resp
    })

@job_endpoints.route('/<uuid>/logs', methods=['GET'])
def get_job_logs(uuid):
    skip_int = 0
    limit_int = 30
    try:
        limit_int, skip_int = get_pagination(request)
    except ValueError:
        return abort(400)
    
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        return abort(404)
    log_count, log_list = job.get_logs(skip=skip_int, limit=limit_int)
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": {
            "logs": log_list,
            "total": log_count
        }
    })

@job_endpoints.route('/<uuid>/reports', methods=['GET'])
def get_job_reports(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        return abort(404)

    file_uuid = request.args.get('file')
    resp = job.get_reports(file_uuid=file_uuid)

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

@job_endpoints.route('/<uuid>/signatures', methods=['GET'])
def get_job_signatures(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    job.load_matches()
    if job.uuid == None:
        return abort(404)

    file_uuid = request.args.get('file')
    matches = job.get_matches(file_uuid=file_uuid)

    dict_list = []
    for match_item in matches:
        dict_list.append(match_item.to_dict(full=True))

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": dict_list
    })

@job_endpoints.route('/<uuid>/exec_instances', methods=['GET'])
def get_job_exec_instances(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        return abort(404)
    resp = job.get_exec_instances()

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

@job_endpoints.route('/<uuid>/details', methods=['GET'])
def get_job_details(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        return abort(404)
    plugin_details = job.plugins

    job_data = {
        "plugins": plugin_details
    }

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": job_data
    })


@job_endpoints.route('/<uuid>/export/<plugin_name>', methods=['POST'])
def get_job_export_plugin(uuid, plugin_name):

    request_data = request.get_json()

    current_app._db.lock()

    # Load the job
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    job.load_matches()
    if job.uuid == None:
        current_app._db.unlock()
        return json_resp_not_found("Could not find job")
    
    
    # Load the plugin
    plugin = current_app._manager.get_plugin(plugin_name)
    if plugin is None:
        current_app._db.unlock()
        return json_resp_not_found("Could not find plugin")
    
    plugin_args = {}
    if 'options' in request_data['export_items']:
        plugin_args = request_data['export_items']['options']
    # Init plugin
    init_plugin = plugin(current_app._manager, args=plugin_args)
    # current_app._manager.initialize_plugins([])[0]

    export_name, export_type = init_plugin.get_export_metadata()

    new_export = job.generate_export_file(export_name, plugin_name, export_type, g.req_username)

    new_export.set_event_filter(request_data['export_items']['events'])
    new_export.set_file_filter(request_data['export_items']['files'])
    new_export.set_network_filter(request_data['export_items']['network'])

    # Run plugin
    export_ok, export_data = init_plugin.export(job, new_export)


    if export_ok == True:
    
        current_app._db.unlock()

        # Save file to filestore
        file_io = new_export.create_file()
        file_io.write(export_data)
        new_export.close_file()

        current_app._db.lock()
        new_export.save()
        current_app._db.unlock()

        new_token = generate_download_token(current_app, g, new_export.uuid)
        return jsonify({
            "ok": True,
            "result": {
                "download_token": new_token,
                "export_uuid": new_export.uuid
            }
        })

    else:
        return json_resp_invalid("Export plugin failed: " + export_ok)


# @job_endpoints.route('/<uuid>/export/<export_uuid>', methods=['POST'])
# def get_job_export_file(uuid, plugin_name):