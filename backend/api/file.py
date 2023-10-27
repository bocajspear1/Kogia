import io
import zipfile
import secrets

import pyzipper

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.submission import SubmissionFile

file_endpoints = Blueprint('file_endpoints', __name__)

#
# File API endpoints
#

@file_endpoints.route('/<uuid>/info', methods=['GET'])
def get_file_info(uuid):
    file_info = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    file_info.load(current_app._db)
    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": file_info.to_dict()
    })

@file_endpoints.route('/<uuid>/gettoken', methods=['GET'])
def get_file_token(uuid):
    file_info = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    file_info.load(current_app._db)

    # TODO: Perform any file access permissions here, as /download doesn't have the user info
    

    if file_info.uuid == None:
        current_app._db.unlock()
        return abort(404)
    
    current_app._db.lock()
    
    # Get file token lock
    current_app._file_tokens_lock.acquire()

    # Generate new token
    new_token = g.req_username + ":" + secrets.token_hex(48)

    found = False
    # Replace any other token from this user
    for i in range(len(current_app._file_tokens)):
        token = current_app._file_tokens[i]
        if token.startswith(f"{g.req_username}:"):
            found = True
            current_app._file_tokens[i] = new_token
    
    if not found:
        current_app._file_tokens.append(new_token)
    current_app._file_tokens_lock.release()
    return jsonify({
        "ok": True,
        "result": {
            "file_token": new_token
        }
    })

@file_endpoints.route('/<uuid>/download', methods=['GET'])
def download_file(uuid):
    file_info = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    file_info.load(current_app._db)
    

    if file_info.uuid == None:
        current_app._db.unlock()
        return abort(404)

    ret_format = request.args.get('format')

    

    if ret_format is None or ret_format not in ('raw', 'zip', 'enczip', 'hex'):
        return jsonify({
            "ok": False,
            "error": "'format' parameter must be set to 'raw', 'zip', 'enczip', or 'hex'."
        })
    raw_file = file_info.open_file()

    if ret_format == 'zip' or ret_format == 'enczip':
        new_zip = None
        out_stream = io.BytesIO()

        if ret_format == 'enczip':
            new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
            new_zip.setpassword(current_app._config['default_zip_password'].encode('utf-8'))
        elif ret_format == 'zip':
            new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

        new_zip.writestr(file_info.name, raw_file.read())
        file_info.close_file()

        new_zip.close()
        out_stream.seek(0)
        current_app._db.unlock()
        return send_file(out_stream, mimetype='application/zip', as_attachment=True,
                         download_name=f"{file_info.name}.zip")
    elif ret_format == 'raw' or ret_format == 'hex':
        if ret_format == 'raw':
            current_app._db.unlock()
            return send_file(raw_file, mimetype='application/octet-stream', as_attachment=True,
                            download_name=f"{file_info.name}_")
        else:
            hex_data = raw_file.read().hex()
            raw_file.close()
            return hex_data.encode('utf-8')
    else:
        raw_file.close_file()
        current_app._file_tokens_lock.acquire()
        current_app._file_tokens.remove(new_token)
        current_app._file_tokens_lock.release()
        abort(500)
        

    
    

@file_endpoints.route('/<uuid>/metadata/list', methods=['GET'])
def get_file_metadata_types(uuid):
    file_obj = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    file_obj.load(current_app._db)
    file_obj.load_metadata(current_app._db)
    current_app._db.unlock()

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

@file_endpoints.route('/<uuid>/metadata/<metatype>/list', methods=['GET'])
def get_file_metadata_list(uuid, metatype):
    file_obj = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    file_obj.load(current_app._db)
    file_obj.load_metadata(current_app._db)
    current_app._db.unlock()

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

@file_endpoints.route('/<uuid>/resubmit', methods=['POST'])
def resubmit_file(uuid):
    resub_file = SubmissionFile(uuid=uuid, filestore=current_app._filestore)
    current_app._db.lock()
    resub_file.load(current_app._db)
    current_app._db.unlock()

    

    # submission_dir = current_app._config['kogia']['submission_dir']

    # re_submission = Submission.new(submission_dir)

    # filename = secure_filename(resub_file.name)
    # new_file = re_submission.generate_file(filename)
    # current_app._db.lock()
    # file.save(new_file.file_path)
    # current_app._db.unlock()
    # new_file.set_read_only()
    # new_submission.add_file(new_file)

    
    # re_submission.description = "Resubmit of "

    # re_submission.name = request.form['name']

    return jsonify({
        "ok": True,
        "result": resub_file.to_dict(full=True)
    })

