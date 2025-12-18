import secrets
import importlib
import os
import logging
import logging.config
import re

from backend.lib.plugin_manager import PluginManager
from backend.lib.db import ArangoConnectionFactory

def safe_uuid(raw_uuid):
    if raw_uuid is None:
        return raw_uuid
    raw_uuid = str(raw_uuid)
    raw_uuid = re.sub(r'[^-_\w]', '', raw_uuid)
    return raw_uuid


def get_logging_config(config):

    log_path = "./logs"
    if 'logpath' in config:
        log_path = config['logpath']

    log_level = config.get('log_level', 'info').upper()
    format_str = "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s"
    if log_level == "DEBUG":
        format_str = "%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "custom": {
                "format": format_str,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                # "style": "{",
                "use_colors": True,
            },
            "custom-file": {
                "format": format_str,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                # "style": "{",
                "use_colors": False,
            },
            'access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'fmt': '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                "use_colors": False,
            }
        },
        "handlers": {
            "console": {
                "level": log_level,
                "formatter": "custom",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",  # Default is stderr
            },
            "file": {
                "level": log_level,
                "formatter": "custom-file",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_path, "kogia.log"), 
            },
            "file-access": {
                "level": log_level,
                "formatter": "access",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_path, "kogia-access.log"), 
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "file-access"],
                "level": log_level,
                "propagate": False,
            },
            "urllib3.connectionpool": { # Noisy, so we suppress
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "PIL.PngImagePlugin": { # Noisy, so we suppress
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "pika": { # Noisy, so we suppress
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "watchfiles.main": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": log_level,
            "propagate": False,
        }
    }

def configure_logging(config, extra=None):
    
    level = logging.INFO
    logformat = "%(asctime)s %(levelname)s: (%(name)s) %(message)s"
    if 'loglevel' in config:
        loglevel = config['loglevel']
        if 'debug' in loglevel.lower():
            logformat = "%(asctime)s %(levelname)s (%(name)s:%(filename)s:%(lineno)d): %(message)s"
            level = logging.DEBUG
            if loglevel.lower() != 'debugall':
                logging.getLogger("requests").setLevel(logging.WARNING)
                logging.getLogger("urllib3").setLevel(logging.WARNING)
                logging.getLogger("PIL").setLevel(logging.WARNING)
                logging.getLogger("pika").setLevel(logging.WARNING)

        elif loglevel.lower() == 'info':
            level = logging.INFO
        elif loglevel.lower() == 'error':
            level = logging.ERROR

    log_path = "./logs"
    if 'logpath' in config:
        log_path = config['logpath']
    
    log_name = "kogia.log"
    if extra is not None:
        log_name = f"kogia-{extra}.log"
    full_log_path = os.path.join(log_path, log_name)

    logging.basicConfig(
        level=level,
        format=logformat,
        handlers=[
            logging.FileHandler(full_log_path),
            logging.StreamHandler()
        ],
    )

def generate_download_token(current_app, file_uuid):
    # Get file token lock
    current_app._download_tokens_lock.acquire()

    # Generate new token
    new_token = current_app.req_username + ":" + file_uuid + ":" + secrets.token_hex(48)

    found = False
    # Replace any other token from this user
    for i in range(len(current_app._download_tokens)):
        token = current_app._download_tokens[i]
        if token.startswith(f"{current_app.req_username}:"):
            found = True
            current_app._download_tokens[i] = new_token
    
    if not found:
        current_app._download_tokens.append(new_token)
    current_app._download_tokens_lock.release()
    return new_token

def get_filestore_modules(filestore_dir="filestore"):
    if not filestore_dir.startswith("/"):
        filestore_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", filestore_dir)
    dir_list = os.listdir(filestore_dir)
    filestore_modules = []

    for file_item in dir_list:
        if not file_item.endswith(".py"):
            continue
        module_name = file_item.replace(".py", "")
        temp_module = importlib.import_module("backend.filestore." + module_name)

        module_items = dir(temp_module)
        for item in module_items:
            if item.startswith("FileStore"):
                filestore_modules.append(getattr(temp_module, item))
    return filestore_modules

def get_worker_modules(worker_dir="worker"):
    if not worker_dir.startswith("/"):
        worker_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", worker_dir)
    dir_list = os.listdir(worker_dir)
    worker_modules = []

    for file_item in dir_list:
        if not file_item.endswith(".py"):
            continue
        module_name = file_item.replace(".py", "")
        temp_module = importlib.import_module("backend.worker." + module_name)

        module_items = dir(temp_module)
        for item in module_items:
            if item.startswith("Worker"):
                worker_modules.append(getattr(temp_module, item))
    return worker_modules

def prepare_all(config, check=True):

    dbf = ArangoConnectionFactory(
        config['db']['host'], 
        config['db']['port'], 
        config['db']['user'], 
        config['db']['password'],
        config['db']['db_name'],
        ssl=bool(config['db'].get('ssl', False)),
        ssl_verify=bool(config['db'].get('verify', True))
    )

    plugin_dirs = []
    if 'plugin_dirs' not in config:
        plugin_dirs.append("./plugins")
    else:
        plugin_dirs += config['plugin_dirs']

    pm = None
    if 'docker_registry' in config and config['docker_registry'] != '':
        pm = PluginManager(plugin_dirs, registry=config['docker_registry'])
    else:
        pm = PluginManager(plugin_dirs)
    pm.load_all(check=check)

    # Load filestore modules
    filestore = None
    available_filestores = get_filestore_modules()

    loaded_filestore = False
    for filestore_class in available_filestores:
        class_name = filestore_class.__name__
        if class_name in config['filestore'] and loaded_filestore == False:
            filestore = filestore_class(config['filestore'][class_name])
            loaded_filestore = True
    
    if not loaded_filestore:
        raise ValueError("Filestore not set")
    
    available_workers = get_worker_modules()
    workers = []
    
    # Load worker modules
    for worker_class in available_workers:
        class_name = worker_class.__name__
        if class_name in config['worker']:
            workers.append(worker_class(config['worker'][class_name], dbf, filestore, pm))

    if len(workers) == 0:
        raise ValueError("No workers were loaded!")
    
    return dbf, pm, filestore, workers