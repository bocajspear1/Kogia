

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import ExecInstance
from backend.version import VERSION 
from backend.lib.system import get_system_string, get_local_storage, get_memory_usage, get_cpu_usage

system_endpoints = Blueprint('system_endpoints', __name__)

@system_endpoints.route('/version')
def version():
    return jsonify({
        "ok": True,
        "result": {
            "version": VERSION
        }
    })

@system_endpoints.route('/stats')
def stats():

    current_app._db.lock()
    submission_count = current_app._db.count('submissions')
    file_count = current_app._db.count('files')
    job_count = current_app._db.count('jobs')
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": {
            "version": VERSION,
            "submission_count": submission_count,
            "file_count": file_count,
            "job_count": job_count
        }
    })

@system_endpoints.route('/usage')
def usage():

    system_string = get_system_string()
    memory_total, memory_used = get_memory_usage()
    storage_total, storage_used = current_app._filestore.get_space()
    local_storage_total, local_storage_used = get_local_storage()

    return jsonify({
        "ok": True,
        "result": {
            "system": system_string,
            "memory_used": memory_used,
            "memory_total": memory_total,
            "cpu_percent": get_cpu_usage(),
            "disk_used": local_storage_used,
            "disk_total": local_storage_total,
            "storage_total": storage_total,
            "storage_used": storage_used,
        }
    })

@system_endpoints.route('/runners')
def runners():

    current_app._db.lock()
    runner_data = current_app._db.all('runners')
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": {
            "runners": list(runner_data)
        }
    })
