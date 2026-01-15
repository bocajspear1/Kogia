import uuid

from backend.lib.job import ExportFile


from fastapi import APIRouter, Request, HTTPException
from fastapi import Form, File, UploadFile, Query
from fastapi.responses import Response

from backend.lib.data import ExecInstance

router = APIRouter(tags=['export'])

#
# Report API endpoints
#

@router.get('/{export_uuid}/download')
def get_export(req: Request, export_uuid: uuid.UUID):

    if hasattr(req.state, "file_uuid") and str(export_uuid) != str(req.state.file_uuid):
        raise HTTPException(400, detail="File does not match token UUID")

    
    with req.app._db.lock:
        export_file = ExportFile(uuid=export_uuid, filestore=req.app._filestore, db=req.app._db)
        export_file.load(req.app._manager)
        if not export_file.found:
            raise HTTPException(404, detail="Export not found")

    raw_file = export_file.open_file()

    out_headers = {'Content-Disposition': f'attachment; filename="{export_file.name}_"'}
    return Response(content=raw_file.read(), media_type=export_file.file_type, headers=out_headers)
