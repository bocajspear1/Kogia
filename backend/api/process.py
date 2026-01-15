from fastapi import APIRouter, Request, HTTPException
from backend.lib.data import Process

from .types import OptionalStrParam, SyscallList, ProcessEventList, ProcessEvent, MetadataList, MetadataItem, MetadataMap

import uuid

router = APIRouter(tags=['process'])
#
# Process API endpoints
#

@router.get('/{uuid}/events')
def get_process_events(req: Request, uuid: uuid.UUID, 
                       type : OptionalStrParam = None,
                       info : OptionalStrParam = None,
                       data : OptionalStrParam = None,
                       skip: int = 0, limit: int  = 30) -> ProcessEventList:
    with req.app._db.lock:
        proc = Process(uuid=uuid)
        proc.load(req.app._db)
        if not proc.found:
            req.app._db.unlock()
            raise HTTPException(404, detail="Process not found")
        
        proc.load_events(req.app._db, as_dict=True, skip=skip, limit=limit,
                        type_filter=type, info_filter=info, data_filter=data)
    
    event_list = []
    for event in proc.events:
        event_list.append(ProcessEvent(**event))
    
    

    return ProcessEventList(events=event_list, total=proc.event_total)

@router.get('/{uuid}/syscalls')
def get_process_syscalls(req: Request, uuid: uuid.UUID, skip: int=0, limit: int =30) -> SyscallList:
    with req.app._db.lock:
        proc = Process(uuid=uuid)
        proc.load(req.app._db)
        if not proc.found:
            raise HTTPException(404, detail="Process not found")
        
        proc.load_syscalls(req.app._db, skip=skip, limit=limit)

    

    return SyscallList(syscalls=proc.syscalls, total=proc.syscall_total)
    
@router.get('/{uuid}/metadata/{metatype}/list')
def get_process_metadata_list(req: Request, uuid: uuid.UUID, metatype: str, filter: OptionalStrParam = None, skip: int = 0, limit: int = 30) -> MetadataList:
    
    proc = Process(uuid=uuid)
    with req.app._db.lock:
        proc.load(req.app._db)
        if not proc.found:
            req.app._db.unlock()
            raise HTTPException(404, detail="Process not found")

        proc.load_metadata(req.app._db, mtype=metatype.strip(), skip=skip, limit=limit, filter=filter, as_dict=True)


    metadata_list = []
    for metadata in proc.metadata:
        metadata_list.append(MetadataItem(**metadata))

            
    return MetadataList(items=metadata_list, total=proc.metadata_total)

@router.get('/{uuid}/metadata/list')
def get_process_metadata_types(req: Request, uuid: uuid.UUID) -> MetadataMap:
    proc = Process(uuid=uuid)
    with req.app._db.lock:
        proc.load(req.app._db)
        proc.load_metadata(req.app._db)

    return_map = {}

    metadata = proc.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    

    return return_map
