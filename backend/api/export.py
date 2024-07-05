from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.job import ExportFile
from backend.api.helpers import get_pagination, json_resp_invalid, json_resp_not_found

export_endpoints = Blueprint('export_endpoints', __name__)

#
# Report API endpoints
#

@export_endpoints.route('/<uuid>/download', methods=['GET'])
def get_export(uuid):

    if hasattr(g, "file_uuid") and uuid != g.file_uuid:
        return json_resp_invalid("Token UUID does not match requested file")
    
    current_app._db.lock()
    export_file = ExportFile(uuid=uuid, filestore=current_app._filestore, db=current_app._db)
    export_file.load(current_app._manager)
    if export_file.uuid == None:
        return json_resp_not_found("Export file not found")

    current_app._db.unlock()

    raw_file = export_file.open_file()

    return send_file(raw_file, mimetype=export_file.file_type, as_attachment=True,
                         download_name=export_file.name)
