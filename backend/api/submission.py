import io
import zipfile
import secrets

import pyzipper

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from werkzeug.utils import secure_filename

from backend.lib.job import Job
from backend.lib.submission import Submission
from backend.lib.workers import JobWorker
from backend.lib.helpers import generate_download_token

submission_endpoints = Blueprint('submission_endpoints', __name__)

#
# Submission API endpoints
#

@submission_endpoints.route('/new', methods=['POST'])
def submit_sample():

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
        current_app.logger.info("Got multiple files")
        multiple = True
    else:
        current_app.logger.info("Got single file")
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


    new_submission = Submission.new(current_app._filestore, g.req_username)

    if 'description' in request.form:
        new_submission.description = request.form['description']

    new_submission.name = request.form['name']

    for uploaded_file in file_list:
        filename = secure_filename(uploaded_file.filename)
        new_file = new_submission.generate_file(filename)

        # Save file to filestore
        file_io = new_file.create_file()
        uploaded_file.save(file_io)
        new_file.close_file()

        current_app._db.lock()
        
        new_submission.add_file(new_file)
        new_file.save(current_app._db)
        # Don't need to load_metadata, since a generate_file initialies metadata

        current_app._db.unlock()

    current_app._db.lock()
    new_submission.save(current_app._db)
    current_app._db.unlock()

    print("new_submission.files", new_submission.files)


    new_job = Job.new(new_submission, None, current_app._db_factory.new(), current_app._filestore)
    # No primary is set, since we are just identifying
    identify_plugins = current_app._manager.get_plugin_list('identify')
    new_job.add_plugin_list(identify_plugins)
    unarchive_plugins = current_app._manager.get_plugin_list('unarchive')
    new_job.add_plugin_list(unarchive_plugins)
    new_job.save()

    new_worker = JobWorker(current_app._manager, new_job)
    current_app._workers.append(new_worker)
    new_worker.start()

    return jsonify({
        "ok": True,
        "result": {
            "submission_uuid": str(new_submission.uuid),
            "job_uuid": str(new_job.uuid)
        }
    })

@submission_endpoints.route('/<uuid>/info', methods=['GET'])
def get_submission_info(uuid):
    submission = Submission(uuid=uuid)
    current_app._db.lock()
    submission.load(current_app._db)
    if submission.uuid == None:
        current_app._db.unlock()
        return abort(404)
    submission.load_files(current_app._db, current_app._filestore)
    if submission.uuid == None:
        current_app._db.unlock()
        return abort(404)
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submission.to_dict(files=True)
    })

@submission_endpoints.route('/<uuid>/gettoken', methods=['GET'])
def get_submission_token(uuid):
    submission = Submission(uuid=uuid)
    current_app._db.lock()
    submission.load(current_app._db)

    # TODO: Perform any file access permissions here, as /download doesn't have the user info
    

    if submission.uuid == None:
        current_app._db.unlock()
        return abort(404)
    
    current_app._db.lock()
    
    new_token = generate_download_token(current_app, g)
    return jsonify({
        "ok": True,
        "result": {
            "download_token": new_token
        }
    })

@submission_endpoints.route('/<uuid>/download', methods=['GET'])
def download_submission(uuid):
    submission = Submission(uuid=uuid)
    current_app._db.lock()
    submission.load(current_app._db)
    if submission.uuid == None:
        current_app._db.unlock()
        return abort(404)

    nopassword = request.args.get('nopassword')

    submission.load_files(current_app._db, current_app._filestore)

    new_zip = None
    out_stream = io.BytesIO()

    if nopassword is None:
        new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        new_zip.setpassword(current_app._config['default_zip_password'].encode('utf-8'))
    else:
        new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

    

    for file in submission.files:
        file_handle = file.open_file()
        new_zip.writestr(file.name, file_handle.read())
        file.close_file()

    new_zip.close()
    out_stream.seek(0)

    current_app._db.unlock()
    return send_file(out_stream, mimetype='application/zip', as_attachment=True,
                     download_name=f"{submission.uuid}.zip")

@submission_endpoints.route('/list', methods=['GET'])
def get_submission_list():
    
    current_app._db.lock()
    file_uuid = request.args.get('file')
    submissions = []
    if file_uuid is not None:
        submissions = Submission.list_dict(current_app._db, file_uuid=file_uuid)
    else:
        submissions = Submission.list_dict(current_app._db)
    current_app._db.unlock()
    return jsonify({
        "ok": True,
        "result": submissions
    })
