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

from fastapi_offline import FastAPIOffline
from fastapi import File, Form, UploadFile, HTTPException, Request, Depends, Security, APIRouter
from fastapi.security import APIKeyHeader

import backend.api.system
import backend.api.plugin
import backend.api.auth
import backend.api.submission
import backend.api.job
import backend.api.report
import backend.api.process
import backend.api.file
import backend.api.analysis
import backend.api.execinstance
import backend.api.docs
import backend.api.export
import backend.api.explore


from backend.auth.db import DBAuth
from backend.version import VERSION

from backend.lib.config import load_config
from backend.auth import ROLES
from backend.lib.helpers import prepare_all, get_logging_config
from backend.lib.workers import WorkerManager

DESCRIPTION="""
Kogia is a highly extensible modular malware analysis framework. 

With its plugin-based design, an extendable web UI, REST API, and flexible graph-based data structure, 
Kogia can support a wide variety of malware analysis pipelines and supports all the functionality needed to easily store, 
analyze, compare, and explore malware.
"""

api_key = APIKeyHeader(name="X-Kogia-API-Auth", auto_error=False)

async def handle_api_key(req: Request, key: str = Security(api_key)):

    ok = False

    if req.client.host in ("testclient",):
        req.app.req_username = "localapi"
        ok = True
    elif req.url.path in ("/api/v1/authenticate",):
        ok = True
    # Extra checks ensure we won't use this for endpoints other then download endpoints
    elif 'download_token' in req.query_params and req.method == "GET" and req.url.path.endswith("/download"):
        download_token = req.query_params['download_token']
        req.app._download_tokens_lock.acquire()
        if download_token in req.app._download_tokens:
            # Pass to API endpoint the file UUID to ensure we aren't downloading a different file
            # TODO: Check if this is thread safe
            req.state.file_uuid = download_token.split(":")[1]
            req.app._download_tokens.remove(download_token)
            req.app._download_tokens_lock.release()
            ok = True
        else:
            req.app._download_tokens_lock.release()
            ok = False
    elif req.app._auth is not None:
        ok, username, roles = req.app._auth.authenticate_existing(key)
        if not ok:
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid API key"
            )
        else:
            req.app.req_username = username
            req.app.req_roles = roles

    if not ok:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API key"
        )
    elif req.app._auth is not None:
        yield key

def create_app(config_path="./config.json"):

    if 'KOGIA_CONFIG_PATH' in os.environ:
        config_path = os.environ['KOGIA_CONFIG_PATH']

    config_data = load_config(config_path)

    logging.config.dictConfig(get_logging_config(config_data))

    app = FastAPIOffline(
        title="Kogia Malware Analysis Server",
        version=VERSION,
        description=DESCRIPTION
    )

    app._config = config_data

    app.logger = logging.getLogger("server")

    app.logger.info("Loaded config file from %s", config_path)

    app._download_tokens = []
    app._download_tokens_lock = threading.RLock()

    app._queue = queue.Queue()

    dbf, pm, filestore, workers = prepare_all(app._config)
    app._manager = pm
    app._db_factory = dbf
    app._db = app._db_factory.new()
    app._filestore = filestore
    app._docs_dir = os.path.abspath(app._config['docs_dir'])

    app._auth = None
    if 'DBAuth' in app._config['auth']:
        app.logger.info("Enabling local DB authentication")
        app._auth = DBAuth(app._db_factory.new())
    else:
        app.logger.info("No authentication configured")

    app._worker_manager = WorkerManager()
    for worker in workers:
        app.logger.info("Loaded worker module %s", worker.__class__.__name__)
        app._worker_manager.add_worker(worker)
        worker.start_worker_senders()
    
    app.logger.info("Server %s started", VERSION)

    app.include_router(
        backend.api.auth.router,
        prefix="/api/v1/authenticate"
    )

    app.include_router(
        backend.api.system.router,
        prefix="/api/v1/system",
        dependencies=[
            Depends(handle_api_key),
        ]
    )

    app.include_router(
        backend.api.submission.router,
        prefix="/api/v1/submission",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.plugin.router,
        prefix="/api/v1/plugin",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.job.router,
        prefix="/api/v1/job",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.report.router,
        prefix="/api/v1/report",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.process.router,
        prefix="/api/v1/process",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.file.router,
        prefix="/api/v1/file",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.analysis.router,
        prefix="/api/v1/analysis",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.execinstance.router,
        prefix="/api/v1/exec_instance",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.docs.router,
        prefix="/api/v1/docs",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.export.router,
        prefix="/api/v1/export",
        dependencies=[
            Depends(handle_api_key),
        ]
    )
    app.include_router(
        backend.api.explore.router,
        prefix="/api/v1/explore",
        dependencies=[
            Depends(handle_api_key),
        ]
    )

    return app