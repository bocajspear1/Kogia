"""Contains helpers purely for the API

"""

from flask import jsonify

def get_pagination(request):
    """Helper to get the parameters 'skip' and 'limit' for pagination.

    Defaults to skip of 0 and limit of 30. 

    It's recommended to catch the ValueError Exception in case the parameters are not numbers
    
    Returns:
        limit, skip
    """
    skip_int = 0
    limit_int = 30
    if request.args.get('skip') is not None:
        skip_int = int(request.args.get('skip'))
    if request.args.get('limit') is not None:
        limit_int = int(request.args.get('limit'))
        
    return limit_int, skip_int

def json_resp_ok(data):
    return jsonify({
        "ok": True,
        "result": data
    }), 200

def json_resp_not_found(message):
    return jsonify({
        "ok": False,
        "error": message
    }), 404

def json_resp_invalid(message):
    return jsonify({
        "ok": False,
        "error": message
    }), 400

def json_resp_failed(message):
    return jsonify({
        "ok": False,
        "error": message
    }), 500