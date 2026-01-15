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
# File API endpoints
#

@router.get('/list')
def get_file_list(req : Request, skip: int = 0, limit: int = 30, q : OptionalStrParam = None) -> SubmissionFileList:
    
    with req.app._db.lock:
        result_list, file_count = SubmissionFile.list_dict(req.app._db, skip=skip, limit=limit, search=q)
    

    file_list = []
    for item in result_list:
        file_list.append(SubmissionFileItem(**item))

    return SubmissionFileList(files=file_list, total=file_count)

@router.get('/{file_uuid}/info')
def get_file_info(req : Request, file_uuid : uuid.UUID) -> SubmissionFileItem:
    file_info = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
    with req.app._db.lock:
        file_info.load(request.app._db)
    

    if not file_info.found:
        raise HTTPException(404, detail="File not found")

    return SubmissionFileItem(**file_info.to_dict())

@router.get('/{file_uuid}/gettoken')
def get_file_token(req : Request, file_uuid : uuid.UUID) -> DownloadTokenResponse:
    file_info = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
    with req.app._db.lock:
        file_info.load(req.app._db)

    # TODO: Perform any file access permissions here, as /download doesn't have the user info
    
    if not file_info.found:
        raise HTTPException(404, detail="File not found")
    
    new_token = generate_download_token(req.app, file_info.uuid)

    return DownloadTokenResponse(download_token=new_token)

@router.get('/{file_uuid}/download')
def download_file(req : Request, file_uuid : uuid.UUID, format: str):

    if hasattr(req.state, "file_uuid") and str(file_uuid) != str(req.state.file_uuid):
        raise HTTPException(400, detail="File does not match token UUID")

    file_info = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
    with req.app._db.lock:
        file_info.load(req.app._db)
        
        if not file_info.found:
            raise HTTPException(404, detail="File not found")


    if format is None or format not in ('raw', 'zip', 'enczip', 'hex'):
        raise HTTPException(400, detail="'format' parameter must be set to 'raw', 'zip', 'enczip', or 'hex'.")
            
    raw_file = file_info.open_file()

    if format == 'zip' or format == 'enczip':
        new_zip = None
        out_stream = io.BytesIO()

        if format == 'enczip':
            new_zip = pyzipper.AESZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
            new_zip.setpassword(req.app._config['default_zip_password'].encode('utf-8'))
        elif format == 'zip':
            new_zip = zipfile.ZipFile(out_stream, "w", compression=pyzipper.ZIP_DEFLATED)

        new_zip.writestr(file_info.name, raw_file.read())
        file_info.close_file()

        new_zip.close()
        out_stream.seek(0)

        out_headers = {'Content-Disposition': f'attachment; filename="{file_info.name}.zip"'}
        return Response(content=out_stream.read(), media_type='application/zip', headers=out_headers)

    elif format == 'raw' or format == 'hex':
        if format == 'raw':
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
def get_file_metadata_types(req : Request, file_uuid : uuid.UUID) -> MetadataMap:
    file_obj = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
    with req.app._db.lock:
        file_obj.load(req.app._db)
        if not file_obj.found:
            raise HTTPException(404, detail="File not found")
        file_obj.load_metadata(req.app._db)

    return_map = {}

    metadata = file_obj.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    return return_map

@router.get('/{file_uuid}/metadata/{metatype}/list')
def get_file_metadata_list(req : Request, file_uuid : uuid.UUID, metatype: str, filter: OptionalStrParam = None, skip: int = 0, limit: int = 30) -> MetadataList:

    file_obj = SubmissionFile(uuid=file_uuid, filestore=req.app._filestore)
    with req.app._db.lock:
        file_obj.load(req.app._db)
        if not file_obj.found:
            raise HTTPException(404, detail="File not found")
        file_obj.load_metadata(req.app._db, mtype=metatype.strip(), skip=skip, limit=limit, filter=filter, as_dict=True)

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

