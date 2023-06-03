# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys 
import sqlite3
import sys
import logging
import platform
import os
import uuid
import threading
import queue
import time
import binascii
import pyzipper
import zipfile
import io
import json

from flask import Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from werkzeug.utils import secure_filename

from backend.lib.plugin_manager import PluginManager
from backend.lib.submission import Submission, SubmissionFile
from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.workers import JobWorker
from backend.lib.job import Job
from backend.lib.data import Report, ExecInstance, Process


VERSION = '0.0.1'

from flask.logging import default_handler

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ['FLASK_KEY']

    with app.app_context():

        app._workers = []

        app._queue = queue.Queue()
        app._manager = PluginManager()
        app._manager.load_all()

        
        config_file = open("./config.json", "r")
        config_data = json.loads(config_file.read())
        config_file.close()
        app._config = config_data

        app._db_factory = ArangoConnectionFactory(
            app._config['kogia']['db_host'], 
            app._config['kogia']['db_port'], 
            app._config['kogia']['db_user'], 
            app._config['kogia']['db_password'],
            app._config['kogia']['db_name']
        )

        app._db = app._db_factory.new()

        submission_dir = app._config['kogia']['submission_dir']
        if not os.path.exists(submission_dir):
            app.logger.info("Creating submission directory %s", submission_dir)
            os.mkdir(submission_dir)
        
        if os.getenv("KOGIA_DEBUG") is not None:
            app.logger.setLevel(logging.DEBUG)
            app.logger.debug("Debugging is on!")
        else:
            app.logger.setLevel(logging.INFO)
        
        app.logger.info("Server %s started", VERSION)

    return app

app = create_app()

@app.route('/api/v1/submissions/count', methods = ['GET'])
def sample_count():
    pass
    # sample_count = 0
    # if os.path.exists(SAMPLE_DIR):
    #     sample_count = len(os.listdir(SAMPLE_DIR))

    # return jsonify({
    #     "ok": True,
    #     "result": {
    #         "count": sample_count
    #     }
    # }) 

@app.route('/api/v1/_version')
def version():
    return jsonify({
        "ok": True,
        "result": {
            "version": VERSION
        }
    })

@app.route('/api/v1/stats')
def stats():

    app._db.lock()
    submission_count = app._db.count('submissions')
    file_count = app._db.count('files')
    unique_file_count = app._db.count('files', unique_by='')
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": {
            "submission_count": submission_count
        }
    })

@app.route('/api/v1/file/<uuid>/info', methods=['GET'])
def get_file_info(uuid):
    file_info = SubmissionFile(uuid=uuid)
    app._db.lock()
    file_info.load(app._db)
    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": file_info.to_dict()
    })

@app.route('/api/v1/file/<uuid>/download', methods=['GET'])
def download_file(uuid):
    file_info = SubmissionFile(uuid=uuid)
    app._db.lock()
    file_info.load(app._db)
    

    if file_info.uuid == None:
        app._db.unlock()
        return abort(404)

    ret_format = request.args.get('format')

    if ret_format is None or ret_format not in ('raw', 'zip', 'enczip', 'hex'):
        return jsonify({
            "ok": False,
            "error": "'format' parameter must be set to 'raw', 'zip', 'enczip', or 'hex'."
        })

    if ret_format == 'zip' or ret_format == 'enczip':
        new_zip = None
        out_stream = io.BytesIO()

        if ret_format == 'enczip':
            new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
            new_zip.setpassword(app._config['default_zip_password'].encode('utf-8'))
        elif ret_format == 'zip':
            new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

        new_zip.write(file_info.file_path,file_info.name)

        new_zip.close()
        out_stream.seek(0)
        app._db.unlock()
        return send_file(out_stream, mimetype='application/zip', as_attachment=True,
                         download_name=f"{file_info.name}.zip")
    elif ret_format == 'raw' or ret_format == 'hex':
        raw_file = open(file_info.file_path, "rb")
        if ret_format == 'raw':
            app._db.unlock()
            return send_file(raw_file, mimetype='application/octet-stream', as_attachment=True,
                            download_name=f"{file_info.name}_")
        else:
            hex_data = raw_file.read().hex()
            raw_file.close()
            return hex_data.encode('utf-8')
    else:
        abort(500)
        

    
    

@app.route('/api/v1/file/<uuid>/metadata/list', methods=['GET'])
def get_file_metadata_types(uuid):
    file_obj = SubmissionFile(uuid=uuid)
    app._db.lock()
    file_obj.load(app._db)
    file_obj.load_metadata(app._db)
    app._db.unlock()

    return_map = {}

    metadata = file_obj.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    return jsonify({
        "ok": True,
        "result": return_map
    })

@app.route('/api/v1/file/<uuid>/metadata/<metatype>/list', methods=['GET'])
def get_file_metadata_list(uuid, metatype):
    file_obj = SubmissionFile(uuid=uuid)
    app._db.lock()
    file_obj.load(app._db)
    file_obj.load_metadata(app._db)
    app._db.unlock()

    return_list = []

    filter = request.args.get('filter')
    metatype = metatype.strip()

    # Will probably want to make more efficient method later

    metadata = file_obj.metadata 
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

@app.route('/api/v1/file/<uuid>/resubmit', methods=['POST'])
def resumbit_file(uuid):
    resub_file = SubmissionFile(uuid=uuid)
    app._db.lock()
    resub_file.load(app._db)
    app._db.unlock()

    

    # submission_dir = app._config['kogia']['submission_dir']

    # re_submission = Submission.new(submission_dir)

    # filename = secure_filename(resub_file.name)
    # new_file = re_submission.generate_file(filename)
    # app._db.lock()
    # file.save(new_file.file_path)
    # app._db.unlock()
    # new_file.set_read_only()
    # new_submission.add_file(new_file)

    
    # re_submission.description = "Resubmit of "

    # re_submission.name = request.form['name']

    return jsonify({
        "ok": True,
        "result": resub_file.to_dict(full=True)
    })


#
# Submission API endpoints
#

@app.route('/api/v1/submission/new', methods=['POST'])
def submit_sample():

    single_param = 'submission'
    multi_param = 'submissions[]'

    if single_param not in request.files and multi_param not in request.files:   
        return jsonify({
            "ok": False,
            "error": f"Nothing submitted in '{single_param}' or '{multi_param}' parameters"
        })

    multiple = False

    file_list = request.files.getlist(multi_param)

    if file_list is not None and len(file_list) > 0:
        app.logger.info("Got multiple files")
        multiple = True
    else:
        app.logger.info("Got single file")
        single_sample = request.files[single_param]

        if single_sample.filename == '':
            return jsonify({
                "ok": False,
                "error": "No sample submitted in '{single_param}' parameter. Name was blank."
            })
        file_list = [single_sample]


    if 'name' not in request.form or request.form['name'].strip() == "":
        return jsonify({
            "ok": False,
            "error": "Name not set for submission"
        })

    
    
    submission_dir = app._config['kogia']['submission_dir']

    new_submission = Submission.new(submission_dir)

    if 'description' in request.form:
        new_submission.description = request.form['description']

    new_submission.name = request.form['name']

    for file in file_list:
        filename = secure_filename(file.filename)
        new_file = new_submission.generate_file(filename)

        # Save file to filesystem
        file.save(new_file.file_path)

        app._db.lock()
        
        new_file.set_read_only()
        new_submission.add_file(new_file)
        new_file.save(app._db)
        # Don't need to load_metadata, since a generate_file initialies metadata

        app._db.unlock()

    app._db.lock()
    new_submission.save(app._db)
    app._db.unlock()

    print(new_submission.files)


    new_job = Job.new(new_submission, None, app._db_factory.new())
    # No primary is set, since we are just identifying
    identify_plugins = app._manager.get_plugin_list('identify')
    new_job.add_plugin_list(identify_plugins)
    unarchive_plugins = app._manager.get_plugin_list('unarchive')
    new_job.add_plugin_list(unarchive_plugins)
    new_job.save()

    new_worker = JobWorker(app._manager, new_job)
    app._workers.append(new_worker)
    new_worker.start()

    return jsonify({
        "ok": True,
        "result": {
            "submission_uuid": str(new_submission.uuid),
            "job_uuid": str(new_job.uuid)
        }
    })

@app.route('/api/v1/submission/<uuid>/info', methods=['GET'])
def get_submission_info(uuid):
    submission = Submission(uuid=uuid)
    app._db.lock()
    submission.load(app._db)
    submission.load_files(app._db)
    if submission.uuid == None:
        app._db.unlock()
        return abort(404)
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submission.to_dict(files=True)
    })

@app.route('/api/v1/submission/<uuid>/download', methods=['GET'])
def download_submission(uuid):
    submission = Submission(uuid=uuid)
    app._db.lock()
    submission.load(app._db)
    if submission.uuid == None:
        app._db.unlock()
        return abort(404)

    nopassword = request.args.get('nopassword')

    submission.load_files(app._db)

    new_zip = None
    out_stream = io.BytesIO()

    if nopassword is None:
        new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        new_zip.setpassword(app._config['default_zip_password'].encode('utf-8'))
    else:
        new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

    

    for file in submission.files:
        print(file.file_path)
        new_zip.write(file.file_path,file.name)

    new_zip.close()
    out_stream.seek(0)

    app._db.unlock()
    return send_file(out_stream, mimetype='application/zip', as_attachment=True,
                     download_name=f"{submission.uuid}.zip")

@app.route('/api/v1/submission/list', methods=['GET'])
def get_submission_list():
    
    app._db.lock()
    file_uuid = request.args.get('file')
    submissions = []
    if file_uuid is not None:
        submissions = Submission.list_dict(app._db, file_uuid=file_uuid)
    else:
        submissions = Submission.list_dict(app._db)
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submissions
    })

#
# Plugin API endpoints
#

@app.route('/api/v1/plugin/list', methods=['GET'])
def get_plugin_list():
    
    app._db.lock()
    plugins = app._manager.get_plugin_list("*")
    init_plugins = app._manager.initialize_plugins(plugins)
    ret_list = []
    for plugin in init_plugins:
        ret_list.append(plugin.to_dict())
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": ret_list
    })

@app.route('/api/v1/plugin/<plugin_name>/info', methods=['GET'])
def get_plugin(plugin_name):
    
    app._db.lock()
    plugin = app._manager.get_plugin(plugin_name)
    if plugin is None:
        return abort(404)
    init_plugins = app._manager.initialize_plugins([plugin])
    plugin = init_plugins[0]

    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": plugin.to_dict()
    })

@app.route('/api/v1/plugin/<plugin_name>/action/<action>', methods=['GET'])
def run_plugin_action(plugin_name, action):
    
    app._db.lock()
    plugin = app._manager.get_plugin(plugin_name)
    if plugin is None:
        return abort(404)
    init_plugins = app._manager.initialize_plugins([plugin])
    plugin = init_plugins[0]

    if not hasattr(plugin, action):
        return abort(404)

    action_func = getattr(plugin, action)
    output = action_func()

    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": output
    })

#
# Analysis API endpoints
#

@app.route('/api/v1/analysis/new', methods=['POST'])
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

    app._db.lock()

    submission_uuid = request_data[submission_uuid_param]
    primary_file_uuid = request_data[primary_uuid_param]
    submission = Submission(uuid=submission_uuid)
    submission.load(app._db)

    new_job = Job.new(submission, primary_file_uuid, app._db_factory.new())

    for plugin in request_data[plugins_param]:
        if 'name' not in plugin:
            return jsonify({
                "ok": False,
                "error": f"Invalid plugin object (no name field)"
            })
        add_plugin_class = app._manager.get_plugin(plugin['name'])
        
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
    
    new_worker = JobWorker(app._manager, new_job)
    app._workers.append(new_worker)
    new_worker.start()

    return jsonify({
        "ok": True,
        "result": {
            "job_uuid": str(new_job.uuid)
        }
    })


#
# Job API endpoints
#

@app.route('/api/v1/job/list', methods=['GET'])
def get_job_list():
    app._db.lock()
    job_list = []
    submission_uuid = request.args.get('submission')
    if submission_uuid is None:
        job_list = Job.list_dict(app._db)
    else:
        job_list = Job.list_dict(app._db, submission_uuid=submission_uuid)
        
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": job_list
    })

@app.route('/api/v1/job/<uuid>/info', methods=['GET'])
def get_job_status(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    if job.uuid == None:
        return abort(404)
    resp = job.to_dict()
    signature_list = job.get_signatures()
    resp['signature_count'] = len(signature_list)
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": resp
    })

@app.route('/api/v1/job/<uuid>/logs', methods=['GET'])
def get_job_logs(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    if job.uuid == None:
        return abort(404)
    resp = job.get_logs()
    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

@app.route('/api/v1/job/<uuid>/reports', methods=['GET'])
def get_job_reports(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    if job.uuid == None:
        return abort(404)

    file_uuid = request.args.get('file')
    resp = job.get_reports(file_uuid=file_uuid)

    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

@app.route('/api/v1/job/<uuid>/signatures', methods=['GET'])
def get_job_signatures(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    if job.uuid == None:
        return abort(404)

    file_uuid = request.args.get('file')
    resp = job.get_signatures(file_uuid=file_uuid)

    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

@app.route('/api/v1/job/<uuid>/exec_instances', methods=['GET'])
def get_job_exec_instances(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    if job.uuid == None:
        return abort(404)
    resp = job.get_exec_instances()

    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": resp
    })

#
# Report API endpoints
#

@app.route('/api/v1/report/<uuid>', methods=['GET'])
def get_report(uuid):
    app._db.lock()
    report = Report(uuid=uuid)
    report.load(app._db)
    if report.uuid == None:
        return abort(404)

    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": report.to_dict()
    })

#
# Exec Instance API endpoints
#

@app.route('/api/v1/exec_instance/<uuid>', methods=['GET'])
def get_exec_instance(uuid):
    app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(app._db)
    exec_instance.load_processes(app._db)
    if exec_instance.uuid == None:
        return abort(404)

    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": exec_instance.to_dict()
    })

#
# Process API endpoints
#

@app.route('/api/v1/process/<uuid>/events', methods=['GET'])
def get_process_events(uuid):
    app._db.lock()
    proc = Process(uuid=uuid)
    proc.load(app._db)
    if proc.uuid == None:
        app._db.unlock()
        return abort(404)
    proc.load_events(app._db, as_dict=True)
    
    app._db.unlock()

    return jsonify({
        "ok": True,
        "result": proc.events
    })

@app.route('/api/v1/process/<uuid>/metadata/<metatype>/list', methods=['GET'])
def get_process_metadata_list(uuid, metatype):
    proc = Process(uuid=uuid)
    app._db.lock()
    proc.load(app._db)
    if proc.uuid == None:
        app._db.unlock()
        return abort(404)
    proc.load_metadata(app._db)
    app._db.unlock()

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

@app.route('/api/v1/process/<uuid>/metadata/list', methods=['GET'])
def get_process_metadata_types(uuid):
    proc = Process(uuid=uuid)
    app._db.lock()
    proc.load(app._db)
    proc.load_metadata(app._db)
    app._db.unlock()

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

if __name__== '__main__':
    app.run()