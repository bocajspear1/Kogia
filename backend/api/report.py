from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import Report

report_endpoints = Blueprint('report_endpoints', __name__)

#
# Report API endpoints
#

@report_endpoints.route('/<uuid>', methods=['GET'])
def get_report(uuid):
    current_app._db.lock()
    report = Report(uuid=uuid)
    report.load(current_app._db)
    if report.uuid == None:
        return abort(404)

    current_app._db.unlock()

    return jsonify({
        "ok": True,
        "result": report.to_dict()
    })
