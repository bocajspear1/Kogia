import io
import shutil
import uuid
import zipfile

import pyzipper

from fastapi import APIRouter, Request, HTTPException

from backend.lib.data import Process

from .types import SubmissionItem, SubmissionItemList, OptionalStrParam, DownloadTokenResponse, NewSubmissionResponse, OptionalFlagParam

from typing_extensions import Annotated, List, Union

from fastapi import Form, File, UploadFile, Query
from fastapi.responses import Response

from werkzeug.utils import secure_filename

from backend.lib.job import Job
from backend.lib.submission import Submission, SubmissionFile
from backend.lib.helpers import generate_download_token


#
# Submission API endpoints
#


router = APIRouter(tags=['submission'])

@router.post('/new')
def submit_sample(req : Request, 
                  name: Annotated[str, Form()],
                  files: Annotated[Union[None, List[UploadFile], List[str]], Form()] = None, 
                  file: Annotated[Union[None, UploadFile, str], Form()] = None,
                  file_uuids: Annotated[Union[None, List[str]], Form()] = None,
                  description: Annotated[Union[None, str], Form()] = None) -> NewSubmissionResponse:
    
    print(files, file)
    
    if files is not None and files[0] == "":
        files = None

    if file_uuids is not None and file_uuids[0] == "":
        file_uuids = None

    if (files is None and file is None and file_uuids is None) or (files is not None and files[0] == ""):   
        raise HTTPException(400, detail="Files not submitted")

    if file_uuids is not None and len(file_uuids) > 0:

        for file_uuid in file_uuids:
            try:
                uuid.UUID(file_uuid)
            except ValueError:
                raise HTTPException(400, detail="Invalid UUID")
            
        new_submission = Submission.new(req.app._filestore, req.app.req_username)

        new_submission.description = description
        new_submission.name = name

        with req.app._db.lock:
            for file_uuid in file_uuids:


                resubmit_file = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
                resubmit_file.load(req.app._db)
                if resubmit_file.uuid is None:
                    raise HTTPException(404, detail=f"File {file_uuid} not found")
                else:
                    new_submission.add_file(resubmit_file)

            new_submission.save(req.app._db)
        

        return NewSubmissionResponse(submission_uuid=str(new_submission.uuid))

    else:
        file_list = []

        if file is not None:
            req.app.logger.info("Got single file")
            file_list.append(file)

        if files is not None:
            req.app.logger.info("Got multiple files")
            file_list += files

        new_submission = Submission.new(req.app._filestore, req.app.req_username)

        new_submission.description = description
        new_submission.name = name

        with req.app._db.lock:
            new_submission.load_files(req.app._db, req.app._filestore)

            for uploaded_file in file_list:
                filename = secure_filename(uploaded_file.filename)
                new_file = new_submission.generate_file(filename)

                # Save file to filestore
                file_io = new_file.create_file()
                shutil.copyfileobj(uploaded_file.file, file_io)
                new_file.close_file()
                
                new_submission.add_file(new_file)
                new_file.save(req.app._db)
                # Don't need to load_metadata, since a generate_file initializes metadata


        
            new_submission.save(req.app._db)

        with req.app._db.lock:
            new_job = Job.new(new_submission, None, req.app._db_factory.new(), req.app._filestore)
            # No primary is set, since we are just identifying
            identify_plugins = req.app._manager.get_plugin_list('identify')
            new_job.add_plugin_list(identify_plugins)
            unarchive_plugins = req.app._manager.get_plugin_list('unarchive')
            new_job.add_plugin_list(unarchive_plugins)
            unpack_plugins = req.app._manager.get_plugin_list('unpack')
            new_job.add_plugin_list(unpack_plugins)
            new_job.save()

        req.app._worker_manager.assign_job(new_job.uuid)

        return NewSubmissionResponse(submission_uuid=new_submission.uuid, job_uuid=str(new_job.uuid))

@router.get('/list')
def get_submission_list(req : Request, file : OptionalStrParam = None, skip=0, limit=30) -> SubmissionItemList:
    
    with req.app._db.lock:
        file_uuid = file
        submissions = []
        total_count = 0
        if file_uuid is not None:
            submissions, total_count = Submission.list_dict(req.app._db, file_uuid=file_uuid, skip=skip, limit=limit)
        else:
            submissions, total_count = Submission.list_dict(req.app._db, skip=skip, limit=limit)

    ret_list = []
    for submission in submissions:
        if "_key" not in submission:
            submission['_key'] = submission['uuid']
        if 'files' not in submission:
            submission['files'] = None
        ret_list.append(SubmissionItem(**submission))
    
    return SubmissionItemList(submissions=ret_list, total=total_count)

@router.get('/{uuid}/info')
def get_submission_info(req : Request, uuid : str) -> SubmissionItem:
    submission = Submission(uuid=uuid)
    with req.app._db.lock:
        submission.load(req.app._db)
        # "uuid" is set to None is the submission is not found
        if submission.uuid == None:
            raise HTTPException(404, detail="Submission not found")
            
        submission.load_files(req.app._db, req.app._filestore)
        if submission.uuid == None:
            raise HTTPException(404, detail="Submission not found")


    submission_display = SubmissionItem(**submission.to_dict(files=True))
    return submission_display

@router.get('/{submission_uuid}/gettoken')
def get_submission_token(req : Request, submission_uuid : str) -> DownloadTokenResponse:
    """
    Get submission download token. Use this token to download a file.
    """
    submission = Submission(uuid=submission_uuid)
    with req.app._db.lock:
        submission.load(req.app._db)

        # TODO: Perform any file access permissions here, as /download doesn't have the user info
        
        if submission.uuid == None:
            raise HTTPException(404, detail="Submission not found")

    
    new_token = generate_download_token(req.app, submission_uuid)

    return DownloadTokenResponse(download_token=new_token)

@router.get('/{submission_uuid}/download')
def download_submission(req : Request, submission_uuid : str, nopassword : OptionalFlagParam = Query(None, description="Set to disable archive encryption",)):


    if hasattr(req.state, "file_uuid") and str(submission_uuid) != str(req.state.file_uuid):
        raise HTTPException(400, detail="File does not match token UUID")
    
    if nopassword is None:
        nopassword = False

    submission = Submission(uuid=submission_uuid)
    with req.app._db.lock:
        submission.load(req.app._db)
        if submission.uuid == None:
            raise HTTPException(404, detail="Submission not found")

        submission.load_files(req.app._db, req.app._filestore)

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

    
    out_headers = {'Content-Disposition': f'attachment; filename="{submission.uuid}.zip"'}
    return Response(content=out_stream.read(), media_type='application/zip', headers=out_headers)


