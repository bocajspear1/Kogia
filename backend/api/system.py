
from fastapi import APIRouter, Request

from backend.lib.data import ExecInstance
from backend.version import VERSION 
from backend.lib.system import get_system_string, get_local_storage, get_memory_usage, get_cpu_usage

from .types import DataResponse

from typing import List, Any

router = APIRouter(tags=['system'])


class VersionResponse(DataResponse):
    version: str

@router.get('/version')
def version() -> VersionResponse: 
    version = VersionResponse(version=VERSION)
    return version


class StatsResponse(DataResponse):
    version: str
    submission_count: int
    file_count: int
    job_count: int

@router.get('/stats')
def stats(request: Request) -> StatsResponse:

    request.app._db.lock()
    submission_count = request.app._db.count('submissions')
    file_count = request.app._db.count('files')
    job_count = request.app._db.count('jobs')
    request.app._db.unlock()

    stats_resp = StatsResponse(
        version=VERSION,
        submission_count=submission_count,
        file_count=file_count,
        job_count=job_count
    )

    return stats_resp


class UsageResponse(DataResponse):
    system: str
    memory_used: float
    memory_total: float
    cpu_percent: float
    disk_used: float
    disk_total: float
    storage_total: float
    storage_used: float

@router.get('/usage')
def usage(request: Request) -> UsageResponse:

    system_string = get_system_string()
    memory_total, memory_used = get_memory_usage()
    storage_total, storage_used = request.app._filestore.get_space()
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


class RunnersResponse(DataResponse):
    runners: List[Any]

@router.get('/runners')
def runners(request: Request) -> RunnersResponse:

    request.app._db.lock()
    runner_data = request.app._db.all('runners')
    request.app._db.unlock()

    runners = RunnersResponse(runners=list(runner_data))

    return runners
