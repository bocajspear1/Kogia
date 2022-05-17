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

from flask import Flask, g, jsonify, current_app, request, render_template, send_from_directory
from werkzeug.utils import secure_filename

from backend.lib.plugin_manager import PluginManager
from backend.lib.submission import Submission
from backend.lib.db import ArangoConnection, ArangoConnectionFactory
from backend.lib.workers import PluginListWorkerManager

VERSION = '0.0.1'

from flask.logging import default_handler

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ['FLASK_KEY']

    with app.app_context():

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

        app._db.connect()

        app._unarchive_queue = queue.Queue()
        app._identify_queue = queue.Queue()
        identify_plugins = app._manager.get_plugin_list('identify')
        app._unarchive_thread = PluginListWorkerManager(identify_plugins, app._identify_queue, app._db_factory.new(), next_queue=)

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

@app.route('/api/v1/submission/new', methods=['POST'])
def sumbit_sample():

    single_param = 'submission'
    multi_param = 'submissions'

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


    # if multiple and 'primary' not in request.form:
    #     return jsonify({
    #         "ok": False,
    #         "error": "Multiple files submitted, but not primary executable set with 'primary'"
    #     })
    
    submission_dir = app._config['kogia']['submission_dir']

    new_submission = Submission.new(submission_dir)

    app._db.lock()
    new_submission.save(app._db)
    app._db.unlock()

    for file in file_list:
        filename = secure_filename(file.filename)
        new_file = new_submission.add_file(filename)
        app._db.lock()
        file.save(new_file.file_path)
        app._db.unlock()
        new_file.set_read_only()

        app._identify_queue.put((new_submission, new_file))
    
    

    return jsonify({
        "ok": True,
        "result": {
            "uuid": str(new_submission.uuid)
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
        "result": {
            "uuid": submission.uuid,
            "owner": submission.owner,
        }
    })

if __name__== '__main__':
    app.run()