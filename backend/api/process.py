from fastapi import APIRouter, Request, HTTPException
from backend.lib.data import Process

from .types import OptionalStrParam, SyscallList, ProcessEventList, ProcessEvent, MetadataList, MetadataItem, MetadataMap

import uuid

router = APIRouter(tags=['process'])
#
# Process API endpoints
#

@router.get('/{uuid}/events')
def get_process_events(request: Request, uuid: uuid.UUID, 
                       type : OptionalStrParam = None,
                       info : OptionalStrParam = None,
                       data : OptionalStrParam = None,
                       skip: int = 0, limit: int  = 30) -> ProcessEventList:
    request.app._db.lock()
    proc = Process(uuid=uuid)
    proc.load(request.app._db)
    if not proc.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="Process not found")
    
    proc.load_events(request.app._db, as_dict=True, skip=skip, limit=limit,
                     type_filter=type, info_filter=info, data_filter=data)

    request.app._db.unlock()
    
    event_list = []
    for event in proc.events:
        event_list.append(ProcessEvent(**event))
    
    

    return ProcessEventList(events=event_list, total=proc.event_total)

@router.get('/{uuid}/syscalls')
def get_process_syscalls(request: Request, uuid: uuid.UUID, skip: int=0, limit: int =30) -> SyscallList:
    request.app._db.lock()
    proc = Process(uuid=uuid)
    proc.load(request.app._db)
    if not proc.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="Process not found")
    
    proc.load_syscalls(request.app._db, skip=skip, limit=limit)
    
    request.app._db.unlock()

    

    return SyscallList(syscalls=proc.syscalls, total=proc.syscall_total)
    
@router.get('/{uuid}/metadata/{metatype}/list')
def get_process_metadata_list(request: Request, uuid: uuid.UUID, metatype: str, filter: OptionalStrParam = None, skip: int = 0, limit: int = 30) -> MetadataList:
    
    proc = Process(uuid=uuid)
    request.app._db.lock()
    proc.load(request.app._db)
    if not proc.found:
        request.app._db.unlock()
        raise HTTPException(404, detail="Process not found")

    proc.load_metadata(request.app._db, mtype=metatype.strip(), skip=skip, limit=limit, filter=filter, as_dict=True)
    request.app._db.unlock()


    metadata_list = []
    for metadata in proc.metadata:
        metadata_list.append(MetadataItem(**metadata))

            
    return MetadataList(items=metadata_list, total=proc.metadata_total)

@router.get('/{uuid}/metadata/list')
def get_process_metadata_types(request: Request, uuid: uuid.UUID) -> MetadataMap:
    proc = Process(uuid=uuid)
    request.app._db.lock()
    proc.load(request.app._db)
    proc.load_metadata(request.app._db)
    request.app._db.unlock()

    return_map = {}

    metadata = proc.metadata 
    for item in metadata:
        if item.key not in return_map:
            return_map[item.key] = 0
        return_map[item.key] += 1

    

    return return_map
