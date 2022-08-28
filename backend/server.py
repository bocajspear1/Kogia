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
import stat
import random
import json

from flask import Flask, g, jsonify, current_app, request, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename

from backend.lib.plugin_manager import PluginManager
from backend.lib.submission import Submission, SubmissionFile
from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.workers import JobWorker
from backend.lib.job import Job


VERSION = '0.0.1'

from flask.logging import default_handler

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ['FLASK_KEY']

    with app.app_context():

        app._workers = []

        app._queue = queue.Queue()
        app._manager = PluginManager()
        app._manager.load()

        
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

@app.route('/api/v1/submission/new', methods=['POST'])
def sumbit_sample():

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

    app._db.lock()
    new_submission.save(app._db)
    app._db.unlock()

    for file in file_list:
        filename = secure_filename(file.filename)
        new_file = new_submission.generate_file(filename)
        app._db.lock()
        file.save(new_file.file_path)
        app._db.unlock()
        new_file.set_read_only()
        new_submission.add_file(new_file)


    new_job = Job.new(new_submission, None, app._db_factory.new())
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
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submission.to_dict(full=True)
    })

@app.route('/api/v1/submission/list', methods=['GET'])
def get_submission_list():
    
    app._db.lock()
    submissions = Submission.list_dict(app._db)
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submissions
    })

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

@app.route('/api/v1/job/<uuid>/info', methods=['GET'])
def get_job_status(uuid):
    app._db.lock()
    job = Job(app._db, uuid=uuid)
    job.load(app._manager)
    resp = job.to_dict()
    app._db.unlock()
    return jsonify({
        "ok": True,
        "result": resp
    })


if __name__== '__main__':
    app.run()