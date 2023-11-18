from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.submission import Submission
from backend.lib.job import Job

analysis_endpoints = Blueprint('analysis_endpoints', __name__)

#
# Analysis API endpoints
#

@analysis_endpoints.route('/new', methods=['POST'])
def create_analysis_job():

    plugins_param = 'plugins'
    submission_uuid_param = "submission_uuid"
    primary_uuid_param = "primary_uuid"

    request_data = request.get_json()

    if plugins_param not in request_data:   
        return jsonify({
            "ok": False,
            "error": f"No plugins submitted"
        })

    if submission_uuid_param not in request_data:   
        return jsonify({
            "ok": False,
            "error": f"No submission uuid submitted"
        })

    if primary_uuid_param not in request_data:   
        return jsonify({
            "ok": False,
            "error": f"No primary file uuid submitted"
        })

    current_app._db.lock()

    submission_uuid = request_data[submission_uuid_param]
    primary_file_uuid = request_data[primary_uuid_param]
    submission = Submission(uuid=submission_uuid)
    submission.load(current_app._db)

    new_job = Job.new(submission, primary_file_uuid, current_app._db_factory.new(), current_app._filestore)

    for plugin in request_data[plugins_param]:
        if 'name' not in plugin:
            return jsonify({
                "ok": False,
                "error": f"Invalid plugin object (no name field)"
            })
        add_plugin_class = current_app._manager.get_plugin(plugin['name'])
        
        add_plugin = None
        if 'options' in plugin:
            options = plugin['options']
            if not isinstance(options, dict):
                return jsonify({
                    "ok": False,
                    "error": f"Invalid plugin object (options field is not dict)"
                })
            new_job.add_plugin(add_plugin_class, args=options)
        else:
            new_job.add_plugin(add_plugin_class)
        
        
    new_job.save()

    current_app._worker_manager.assign_job(new_job.uuid)

    return jsonify({
        "ok": True,
        "result": {
            "job_uuid": str(new_job.uuid)
        }
    })
