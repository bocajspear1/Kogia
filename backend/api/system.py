import platform

import psutil

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import ExecInstance
from backend.version import VERSION 

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

    system_info = "{} - {} {}".format(platform.node(), platform.system(), platform.release())
    memory = psutil.virtual_memory() 
    main_disk = psutil.disk_usage('/')

    return jsonify({
        "ok": True,
        "result": {
            "system": system_info,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "cpu_percent": psutil.cpu_percent(interval=.5),
            "disk_used": main_disk.used,
            "disk_total": main_disk.total
        }
    })

