from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.job import Job
from backend.api.helpers import get_pagination

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