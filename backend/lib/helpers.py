import secrets
import importlib
import os

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

