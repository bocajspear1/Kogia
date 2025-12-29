import io
import zipfile
import secrets
import uuid

import pyzipper

from backend.lib.submission import SubmissionFile
from backend.lib.helpers import generate_download_token

from fastapi import APIRouter, Request, HTTPException, Response

from backend.lib.data import Process

from .types import OptionalStrParam, SubmissionFileItem, SubmissionFileList, DownloadTokenResponse, MetadataMap, MetadataList, MetadataItem

router = APIRouter(tags=['file'])

#
# Plugin API endpoints
#

@router.get('/{file_uuid}/info')
def get_file_info(request : Request, file_uuid : uuid.UUID) -> SubmissionFileItem:
    file_info = SubmissionFile(uuid=file_uuid, filestore=request.app._filestore)
    request.app._db.lock()
    file_info.load(request.app._db)
    request.app._db.unlock()

    if not file_info.found:
        raise HTTPException(404, detail="File not found")

    return SubmissionFileItem(**file_info.to_dict())

@router.get('/{file_uuid}/gettoken')
def get_file_token(request : Request, file_uuid : uuid.UUID) -> DownloadTokenResponse:
    file_info = SubmissionFile(uuid=file_uuid, filestore=request.app._filestore)
    request.app._db.lock()
    file_info.load(request.app._db)

    # TODO: Perform any file access permissions here, as /download doesn't have the user info
    

    if not file_info.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="File not found")
    
    new_token = generate_download_token(request.app, file_info.uuid)
    request.app._db.unlock()

    return DownloadTokenResponse(download_token=new_token)

@router.get('/{file_uuid}/download')
def download_file(request : Request, file_uuid : uuid.UUID, format: str):

    if hasattr(request.app, "file_uuid") and file_uuid != request.app.file_uuid:
        raise HTTPException(400, detail="File does not match token UUID")

    file_info = SubmissionFile(uuid=file_uuid, filestore=request.app._filestore)
    request.app._db.lock()
    file_info.load(request.app._db)
    
    if not file_info.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="File not found")


    if format is None or format not in ('raw', 'zip', 'enczip', 'hex'):
        raise HTTPException(400, detail="'format' parameter must be set to 'raw', 'zip', 'enczip', or 'hex'.")
            
    raw_file = file_info.open_file()

    if format == 'zip' or format == 'enczip':
        new_zip = None
        out_stream = io.BytesIO()

        if format == 'enczip':
            new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
            new_zip.setpassword(request.app._config['default_zip_password'].encode('utf-8'))
        elif format == 'zip':
            new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

        new_zip.writestr(file_info.name, raw_file.read())
        file_info.close_file()

        new_zip.close()
        out_stream.seek(0)
        request.app._db.unlock()

        out_headers = {'Content-Disposition': f'attachment; filename="{file_info.name}.zip"'}
        return Response(content=out_stream.read(), media_type='application/zip', headers=out_headers)

    elif format == 'raw' or format == 'hex':
        if format == 'raw':
            request.app._db.unlock()

            out_headers = {'Content-Disposition': f'attachment; filename="{file_info.name}_"'}
            return Response(content=raw_file.read(), media_type='application/octet-stream', headers=out_headers)
        else:
            hex_data = raw_file.read().hex()
            raw_file.close()
            return hex_data.encode('utf-8')
    else:
        raw_file.close_file()
        request.app._download_tokens_lock.acquire()
        request.app._download_tokens.remove(new_token)
        request.app._download_tokens_lock.release()
        raise HTTPException(500, detail="Not implemented")
        


@router.get('/{file_uuid}/metadata/list')
def get_file_metadata_types(request : Request, file_uuid : uuid.UUID) -> MetadataMap:
    file_obj = SubmissionFile(uuid=file_uuid, filestore=request.app._filestore)
    request.app._db.lock()
    file_obj.load(request.app._db)
    if not file_obj.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="File not found")
    file_obj.load_metadata(request.app._db)
    request.app._db.unlock()

    return_map = {}

    metadata = file_obj.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    return return_map

@router.get('/{file_uuid}/metadata/{metatype}/list')
def get_file_metadata_list(request : Request, file_uuid : uuid.UUID, metatype: str, filter: OptionalStrParam = None, skip: int = 0, limit: int = 30) -> MetadataList:

    file_obj = SubmissionFile(uuid=file_uuid, filestore=request.app._filestore)
    request.app._db.lock()
    file_obj.load(request.app._db)
    if not file_obj.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="File not found")
    file_obj.load_metadata(request.app._db, mtype=metatype.strip(), skip=skip, limit=limit, filter=filter, as_dict=True)
    request.app._db.unlock()

    metadata_list = []

    for item in file_obj.metadata:
        metadata_list.append(MetadataItem(**item))

            
    return MetadataList(items=metadata_list, total=file_obj.metadata_total)

# @file_endpoints.route('/<uuid>/resubmit', methods=['POST'])
# def resubmit_file(uuid):
#     resub_file = SubmissionFile(uuid=uuid, filestore=request.app._filestore)
#     request.app._db.lock()
#     resub_file.load(request.app._db)
#     request.app._db.unlock()

    

#     # submission_dir = request.app._config['kogia']['submission_dir']

#     # re_submission = Submission.new(submission_dir)

#     # filename = secure_filename(resub_file.name)
#     # new_file = re_submission.generate_file(filename)
#     # request.app._db.lock()
#     # file.save(new_file.file_path)
#     # request.app._db.unlock()
#     # new_file.set_read_only()
#     # new_submission.add_file(new_file)

    
#     # re_submission.description = "Resubmit of "

#     # re_submission.name = request.form['name']

#     return jsonify({
#         "ok": True,
#         "result": resub_file.to_dict(full=True)
#     })

