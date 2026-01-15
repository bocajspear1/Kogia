from backend.lib.objects import Metadata
from backend.lib.submission import SubmissionFile

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(tags=['explore'])

#
# Explore API endpoints
#

@router.get('/search')
def explore_search(req : Request, q : str, t : str, skip: int = 0, limit: int = 30):


    with req.app._db.lock:

        results = []
        if t == 'files':
            results = SubmissionFile.list_dict(req.app._db, skip=skip, limit=limit, search=q) 
        elif t == 'metadata':
            results = Metadata.list_dict(req.app._db, skip=skip, limit=limit, search=q)
        elif t == 'metadata':
            pass
        else:
            raise HTTPException(400, "Invalid search type")



    return json_resp_ok({
        "results": results
    })

@explore_endpoints.route('/connected/<start_type>/<start_uuid>', methods=['GET'])
def explore_connected(start_type, start_uuid):

    skip_int = 0
    limit_int = 50
    try:
        limit_int, skip_int = get_pagination(request)
    except ValueError:
        return json_resp_invalid('Invalid pagination')
    
    query = request.args.get('q')
    item_type = request.args.get('type')
    
    current_app._db.lock()

    results = []
    if start_type == "file":
        start_obj = SubmissionFile(uuid=start_uuid)
        start_obj.load(current_app._db)
        if start_obj.uuid == None:
            current_app._db.unlock()
            return abort(404)
        
        end_collection = ""
        end_filter = None
        filter_edges = []
        if item_type == "files":
            end_collection = SubmissionFile.COLLECTION
            end_filter = SubmissionFile.get_search_tuple(query)
            filter_edges = ['has_metadata', 'has_report']
        elif item_type == 'metadata':
            end_collection = Metadata.COLLECTION
        results = start_obj.get_connected_to(current_app._db, end_collection, filter_vertices=end_filter, 
                                    filter_edges=filter_edges, #['has_metadata',
                                                #  'added_match', 'matched_signature', 'has_process', 'has_event', 
                                                #  'has_exec_instance', 'has_instance_metadata', , 'has_process_metadata'
                                                  #  ],
                                    limit=limit_int, skip=skip_int, return_path=True, max=5)
    current_app._db.unlock()


    return json_resp_ok({
        "results": results
    })