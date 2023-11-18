import secrets
import importlib
import os

from backend.lib.plugin_manager import PluginManager
from backend.lib.db import ArangoConnectionFactory

def generate_download_token(current_app, g):
    # Get file token lock
    current_app._download_tokens_lock.acquire()

    # Generate new token
    new_token = g.req_username + ":" + secrets.token_hex(48)

    found = False
    # Replace any other token from this user
    for i in range(len(current_app._download_tokens)):
        token = current_app._download_tokens[i]
        if token.startswith(f"{g.req_username}:"):
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
        config['db']['db_name']
    )

    pm = PluginManager()
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