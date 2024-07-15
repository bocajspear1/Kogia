# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import sys 
import secrets
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
from backend.api.export import export_endpoints
from backend.api.docs import docs_endpoints

from backend.lib.config import load_config
from backend.auth import ROLES
from backend.lib.helpers import prepare_all

from backend.auth.db import DBAuth
from backend.lib.workers import WorkerManager

from backend.version import VERSION 

from flask.logging import default_handler

from flask import send_from_directory

STATIC_DIR = '../frontend/dist'

app = Flask(__name__, static_url_path='/', static_folder=STATIC_DIR)
flask_key = None
if os.path.exists(".flask_key"):
    flask_key_file = open(".flask_key", "r")
    flask_key = flask_key_file.read().strip()
    flask_key_file.close()
else:
    flask_key = secrets.token_hex(20)
    flask_key_file = open(".flask_key", "w")
    flask_key_file.write(flask_key)
    flask_key_file.close()

app.secret_key = flask_key

AUTH_PATH = '/api/v1/authenticate'
FILE_PATH = "/api/v1/file/"
SUBMISSION_PATH = "/api/v1/submission/"
EXPORT_PATH = "/api/v1/export/"

@app.before_request
def check_req():
    # request is available
   
    download_token = request.args.get('download_token')
    first_item = request.path.split("/")[1]
    if first_item == "":
        return send_from_directory(STATIC_DIR, "index.html")
    if first_item in ("index.html", "css", "assets", "images", "icons"):
        return
    elif not first_item == "api":
        return send_from_directory(STATIC_DIR, "index.html")
    if request.path != AUTH_PATH or download_token is not None:
        if download_token is not None:

            if request.path.startswith(FILE_PATH) or request.path.startswith(SUBMISSION_PATH) or request.path.startswith(EXPORT_PATH) \
                and request.path.endswith("/download"):

                app._download_tokens_lock.acquire()
                if download_token in app._download_tokens:
                    # Pass to API endpoint the file UUID to ensure we aren't downloading a different file
                    g.file_uuid = download_token.split(":")[1]
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
app.register_blueprint(export_endpoints, url_prefix='/api/v1/export')
app.register_blueprint(docs_endpoints, url_prefix='/api/v1/docs')

with app.app_context():

    if os.getenv("KOGIA_DEBUG") is not None:
        app.logger.setLevel(logging.DEBUG)
        app.logger.debug("Debugging is on!")
    else:
        app.logger.setLevel(logging.INFO)


    app._download_tokens = []
    app._download_tokens_lock = threading.RLock()

    app._queue = queue.Queue()

    app._config = load_config("./config.json")

    dbf, pm, filestore, workers = prepare_all(app._config)
    app._manager = pm
    app._db_factory = dbf
    app._db = app._db_factory.new()
    app._filestore = filestore

    # Set docs directory
    app._docs_dir = os.path.abspath(app._config['docs_dir'])
    app.logger.info("Setting documentation directory to %s", app._docs_dir)

    app.logger.info("Loaded filestore %s", filestore.__class__.__name__)

    app._worker_manager = WorkerManager()
    for worker in workers:
        app.logger.info("Loaded worker module %s", worker.__class__.__name__)
        app._worker_manager.add_worker(worker)
        worker.start_worker_senders()


    # Load authentication
    app._auth = None
    if 'DBAuth' in app._config['auth']:
        app.logger.info("Enabling local DB authentication")
        app._auth = DBAuth(app._db_factory.new())
    else:
        app.logger.info("No authentication configured")

    app.logger.info("Server %s started", VERSION)

# return app

# app = create_app()
    
if __name__== '__main__':
    app.run()