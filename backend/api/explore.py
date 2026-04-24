from backend.lib.objects import Metadata
from backend.lib.submission import SubmissionFile
from backend.api.types import ExploreResponse, MetadataList, SignatureMatchList, SubmissionFileList, SubmissionFileItem


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

@router.get('/connected/{start_type}/{start_uuid}')
def explore_connected(req : Request, start_type: str, start_uuid: str, 
                      q : str, endtype : str, skip: int = 0, limit: int = 30) -> ExploreResponse:

    with req.app._db.lock:
    

        results = []
        if start_type == "file":
            start_obj = SubmissionFile(uuid=start_uuid)
            start_obj.load(req.app._db)
            if start_obj.uuid == None:
                raise HTTPException(404, detail="File not found")
                
            
        end_collection = ""
        end_filter = None
        filter_edges = []
        if endtype == "files":
            end_collection = SubmissionFile.COLLECTION
            end_filter = SubmissionFile.get_search_tuple(q)
            filter_edges = ['has_metadata', 'has_report']
        elif endtype == 'metadata':
            end_collection = Metadata.COLLECTION
        results = start_obj.get_connected_to(req.app._db, end_collection, filter_vertices=end_filter, 
                                    filter_edges=filter_edges, #['has_metadata',
                                                #  'added_match', 'matched_signature', 'has_process', 'has_event', 
                                                #  'has_exec_instance', 'has_instance_metadata', , 'has_process_metadata'
                                                #  ],
                                    limit=limit, skip=skip, return_path=True, max=5)
        
        if endtype == "files":
            file_items = []
            for result in results:
                file_items.append(SubmissionFileItem(**result))
            
            return SubmissionFileList(files=file_items, total=0)