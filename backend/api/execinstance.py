from base64 import b64encode
import uuid

from fastapi import APIRouter, Request, HTTPException

from .types import OptionalStrParam, ExecInstanceItem, MetadataItem, MetadataList, MetadataMap, OptionalIntParam, NetCommItem, NetCommList, ScreenshotResponse

from typing_extensions import Annotated, List, Union

from fastapi.responses import Response

from backend.lib.data import ExecInstance

router = APIRouter(tags=['exec_instance'])


#
# Exec Instance API endpoints
#
@router.get('/{uuid}')
def get_exec_instance(req : Request, uuid : uuid.UUID) -> ExecInstanceItem:

    exec_instance = ExecInstance(uuid=uuid)
    req.app._db.lock()
    
    exec_instance.load(req.app._db)
    
    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")

    exec_instance.load_processes(req.app._db)
    req.app._db.unlock()

    exec_inst_dict = exec_instance.to_dict(full=True)

    return ExecInstanceItem(**exec_inst_dict)


@router.get('/{uuid}/metadata/{metatype}/list')
def get_execinstance_metadata_list(req : Request, uuid : uuid.UUID, metatype: str, filter: OptionalStrParam = None, skip: int = 0, limit: int = 50) -> MetadataList:
   

    req.app._db.lock()
    exec_instance = ExecInstance(uuid=uuid)
    exec_instance.load(req.app._db)

    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")

    exec_instance.load_metadata(req.app._db, mtype=metatype.strip(), skip=skip, limit=limit, filter=filter, as_dict=True)
    req.app._db.unlock()

    metadata_list = []

    for item in exec_instance.metadata:
        metadata_list.append(MetadataItem(**item))

    return MetadataList(items=metadata_list, total=exec_instance.metadata_total)

@router.get('/{exec_uuid}/metadata/list')
def get_execinstance_metadata_types(req : Request, exec_uuid : uuid.UUID) -> MetadataMap:
    req.app._db.lock()
    exec_instance = ExecInstance(uuid=exec_uuid)
    exec_instance.load(req.app._db)

    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")
    
    exec_instance.load_metadata(req.app._db)
    req.app._db.unlock()

    return_map = exec_instance.get_metadata_types()

    return return_map

@router.get('/{exec_uuid}/netcomm/list')
def get_execinstance_netcomm(req : Request, exec_uuid : uuid.UUID, address : OptionalStrParam = None, port : OptionalIntParam = None, skip: int = 0, limit: int = 50):

    req.app._db.lock()
    exec_instance = ExecInstance(uuid=exec_uuid)
    exec_instance.load(req.app._db)

    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")
    
    
    exec_instance.load_netcomms(req.app._db, limit=limit, skip=skip, as_dict=True, port_filter=port, address_filter=address)
    comm_stats = exec_instance.network_comm_statistics
    req.app._db.unlock()

    netcomm_list = []
    for item in exec_instance.network_comms:
        netcomm_list.append(NetCommItem(**item))

    return NetCommList(netcomms=netcomm_list, total=exec_instance.network_comms_total, statistics=comm_stats)

@router.get('/{exec_uuid}/thumbnail/{name}')
def get_execinstance_thumbnails(req : Request, exec_uuid : uuid.UUID, name : str):

    req.app._db.lock()
    exec_instance = ExecInstance(uuid=exec_uuid)
    exec_instance.load(req.app._db)

    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")
    req.app._db.unlock()

    if name in exec_instance.screenshots:
        thumb_name = f"{name}-t"
        thumb_file = req.app._filestore.open_file(thumb_name)
        encode_image = b64encode(thumb_file.read()).decode()
        req.app._filestore.close_file(name, thumb_file)
        return ScreenshotResponse(image_data=encode_image, name=thumb_name)
    else:
        raise HTTPException(404, "Screenshot not found")

@router.get('/{exec_uuid}/screenshot/{name}')
def get_execinstance_screenshot(req : Request, exec_uuid : uuid.UUID, name : str):

    req.app._db.lock()
    exec_instance = ExecInstance(uuid=exec_uuid)
    exec_instance.load(req.app._db)

    if not exec_instance.found:
        req.app._db.unlock()
        raise HTTPException(404, "Execution instance not found")
    
    req.app._db.unlock()

    if name in exec_instance.screenshots:
        screenshot_name = f"{name}"
        screenshot_file = req.app._filestore.open_file(name)
        encode_image = b64encode(screenshot_file.read()).decode()
        req.app._filestore.close_file(name, screenshot_file)
        return ScreenshotResponse(image_data=encode_image, name=screenshot_name)
    else:
        raise HTTPException(404, "Screenshot not found")

    