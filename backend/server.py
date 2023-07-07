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

from flask import Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort, Response


from backend.lib.plugin_manager import PluginManager
from backend.lib.db import ArangoConnection, ArangoConnectionFactory

from backend.api.job import job_endpoints
from backend.api.process import process_endpoints
from backend.api.submission import submission_endpoints
from backend.api.file import file_endpoints
from backend.api.analysis import analysis_endpoints
from backend.api.plugin import plugin_endpoints
from backend.api.report import report_endpoints
from backend.api.execinstance import execinstance_endpoints
from backend.api.system import system_endpoints

from backend.auth.db import DBAuth

from backend.version import VERSION 

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

        app._auth = None
        if app._config['kogia']['auth_type'] == "db":
            app.logger.info("Enabling local DB authentication")
            app._auth = DBAuth()
        else:
            app.logger.info("No authentication configured")

    return app

app = create_app()

@app.before_request
def check_req():
    # request is available
    print(request.path)
    if app._auth is not None:
        authkey = request.headers.get('X-Kogia-API-Auth', default=None)

        if authkey is None:
            return Response(response="Unauthorized", status=401)


app.register_blueprint(job_endpoints, url_prefix='/api/v1/job')
app.register_blueprint(process_endpoints, url_prefix='/api/v1/process')
app.register_blueprint(file_endpoints, url_prefix='/api/v1/file')
app.register_blueprint(submission_endpoints, url_prefix='/api/v1/submission')
app.register_blueprint(analysis_endpoints, url_prefix='/api/v1/analysis')
app.register_blueprint(plugin_endpoints, url_prefix='/api/v1/plugin')
app.register_blueprint(report_endpoints, url_prefix='/api/v1/report')
app.register_blueprint(execinstance_endpoints, url_prefix='/api/v1/exec_instance')
app.register_blueprint(system_endpoints, url_prefix='/api/v1/system')


if __name__== '__main__':
    app.run()