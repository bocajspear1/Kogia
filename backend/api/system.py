
from fastapi import APIRouter, Request

from backend.lib.data import ExecInstance
from backend.version import VERSION 
from backend.lib.system import get_system_string, get_local_storage, get_memory_usage, get_cpu_usage

from .types import DataResponse, UsageResponse, VersionResponse, StatsResponse, RunnersResponse

from typing import List, Any

router = APIRouter(tags=['system'])



@router.get('/version')
def version() -> VersionResponse: 
    """
    Get version of the Kogia instance
    """
    version = VersionResponse(version=VERSION)
    return version


@router.get('/stats')
def stats(req: Request) -> StatsResponse:

    with req.app._db.lock:
        submission_count = req.app._db.count('submissions')
        file_count = req.app._db.count('files')
        job_count = req.app._db.count('jobs')

    stats_resp = StatsResponse(
        version=VERSION,
        submission_count=submission_count,
        file_count=file_count,
        job_count=job_count
    )

    return stats_resp


@router.get('/usage')
def usage(req: Request) -> UsageResponse:

    system_string = get_system_string()
    memory_total, memory_used = get_memory_usage()
    storage_total, storage_used = req.app._filestore.get_space()
    local_storage_total, local_storage_used = get_local_storage()

    usage = UsageResponse(
        system=system_string,
        memory_used=memory_used,
        memory_total=memory_total,
        cpu_percent=get_cpu_usage(),
        disk_used=local_storage_used,
        disk_total=local_storage_total,
        storage_total=storage_total,
        storage_used=storage_used,
    )

    return usage

@router.get('/runners')
def runners(req: Request) -> RunnersResponse:

    with req.app._db.lock:
        runner_data = req.app._db.all('runners')

    runners = RunnersResponse(runners=list(runner_data))

    return runners
