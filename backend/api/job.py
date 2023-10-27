from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.job import Job

job_endpoints = Blueprint('job_endpoints', __name__)

#
# Job API endpoints
#

@job_endpoints.route('/list', methods=['GET'])
def get_job_list():
    current_app._db.lock()

    skip_int = 0
    limit_int = 20
    if request.args.get('skip') is not None:
        try:
            skip_int = int(request.args.get('skip'))
        except ValueError:
            return abort(400)
    if request.args.get('limit') is not None:
        try:
            limit_int = int(request.args.get('limit'))
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
        return abort(404)
    resp = job.to_dict()
    signature_list = job.get_signatures()
    resp['signature_count'] = len(signature_list)
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": resp
    })

@job_endpoints.route('/<uuid>/logs', methods=['GET'])
def get_job_logs(uuid):
    current_app._db.lock()
    job = Job(current_app._db, current_app._filestore, uuid=uuid)
    job.load(current_app._manager)
    if job.uuid == None:
        return abort(404)
    resp = job.get_logs()
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
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
    if job.uuid == None:
        return abort(404)

    file_uuid = request.args.get('file')
    resp = job.get_signatures(file_uuid=file_uuid)

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
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
