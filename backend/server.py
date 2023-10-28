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
import json
import secrets

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

from backend.lib.config import load_config
from backend.auth import ROLES
from backend.lib.helpers import get_filestore_modules

from backend.auth.db import DBAuth


from backend.version import VERSION 

from flask.logging import default_handler

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ['FLASK_KEY']

    with app.app_context():

        if os.getenv("KOGIA_DEBUG") is not None:
            app.logger.setLevel(logging.DEBUG)
            app.logger.debug("Debugging is on!")
        else:
            app.logger.setLevel(logging.INFO)

        app._workers = []


        app._download_tokens = []
        app._download_tokens_lock = threading.RLock()

        app._queue = queue.Queue()
        app._manager = PluginManager()
        app._manager.load_all()

        
        
        app._config = load_config("./config.json")

        app._db_factory = ArangoConnectionFactory(
            app._config['kogia']['db_host'], 
            app._config['kogia']['db_port'], 
            app._config['kogia']['db_user'], 
            app._config['kogia']['db_password'],
            app._config['kogia']['db_name']
        )

        app._db = app._db_factory.new()

        # Load filestore modules
        available_filestores = get_filestore_modules()

        loaded_filestore = False
        for filestore_class in available_filestores:
            class_name = filestore_class.__name__
            if class_name in app._config['filestore'] and loaded_filestore == False:
                app.logger.info("Loaded filestore %s", class_name)
                app._filestore = filestore_class(app._config['filestore'][class_name])
                loaded_filestore = True
      
        if not loaded_filestore:
            raise ValueError("Filestore not set")

        # Load authentication
        app._auth = None
        if app._config['kogia']['auth_type'] == "db":
            app.logger.info("Enabling local DB authentication")
            app._auth = DBAuth(app._db_factory.new())
        else:
            app.logger.info("No authentication configured")

        app.logger.info("Server %s started", VERSION)

    return app

app = create_app()

AUTH_PATH = '/api/v1/authenticate'
FILE_PATH = "/api/v1/file/"
SUBMISSION_PATH = "/api/v1/submission/"

@app.before_request
def check_req():
    # request is available
    # print(request.path)
    download_token = request.args.get('download_token')
    if request.path != AUTH_PATH or download_token is not None:
        if download_token is not None:
            if request.path.startswith(FILE_PATH) or request.path.startswith(SUBMISSION_PATH):
                app._download_tokens_lock.acquire()
                if download_token in app._download_tokens:
                    app._download_tokens.remove(download_token)
                    app._download_tokens_lock.release()
                else:
                    app._download_tokens_lock.release()
                    return Response(response="Unauthorized", status=401)
            else:
                return Response(response="Unauthorized", status=401)
        elif app._auth is not None:
            authkey = request.headers.get('X-Kogia-API-Auth', default=None)

            if authkey is None:
                return Response(response="Unauthorized", status=401)
            else:
                ok, username, roles = app._auth.authenticate_existing(authkey)
                if not ok:
                    return Response(response="Unauthorized", status=401)
                else:
                    g.req_username = username
                    g.req_roles = roles
        else:
            g.req_username = 'user'
            g.req_roles = ['admin']


@app.route(AUTH_PATH, methods=['POST'])
def authenticate():
    if app._auth is not None:
        if 'username' not in request.form or request.form['username'].strip() == "":
            return Response(response="Invalid authentication request", status=400)
        if 'password' not in request.form or request.form['password'].strip() == "":
            return Response(response="Invalid authentication request", status=400)

        ok, token, roles = app._auth.authenticate_new(request.form['username'].strip(), request.form['password'].strip())

        if "admin" in roles:
            roles += ROLES

        if not ok:
            return jsonify({
                "ok": False,
                "error": f"Unauthorized: {token}"
            }), 401
        else:
            return jsonify({
                "ok": True,
                "result": {
                    "api_key": token,
                    "roles": roles
                }
            })


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