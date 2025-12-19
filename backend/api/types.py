import uuid

from pydantic import BaseModel

from backend.lib.data import SIGNATURE_SEVERITY

from typing import Generic, List, Union, Type, Optional, TypeVar, Any, Dict

OptionalStrParam = Union[str, None]
OptionalFlagParam = Union[bool, None]

class DataResponse(BaseModel):
    pass

DataType = TypeVar('DataType', bound=DataResponse)

class PluginDisplay(BaseModel):
    name: str
    config: dict
    type: str
    author: str
    display: Any
    options: list
    docs: Union[str, None]

class PluginDisplayList(BaseModel):
    plugins: List[PluginDisplay]


class FileDisplay(BaseModel):
    _key: str
    uuid: str
    name: str
    file_id: str
    dropped: bool
    mime_type: str
    unpacked_archive: bool
    exec_format: str
    exec_type: str
    exec_arch: str
    exec_bits: str
    exec_interpreter: str
    exec_packer: str
    target_os: str
    hash: str
        
class FileDisplayList(BaseModel):
    submissions: List[FileDisplay]

class SubmissionItem(BaseModel):
    _key: str
    uuid: str
    owner: str
    submit_time: int
    name: str
    description: str
    files: Optional[List[FileDisplay]]
        
class SubmissionItemList(BaseModel):
    submissions: List[SubmissionItem]
    total: int

class DownloadTokenResponse(BaseModel):
    download_token: str


class NewSubmissionResponse(BaseModel):
    submission_uuid: uuid.UUID
    job_uuid: Union[uuid.UUID, None]

class NewAnalysisPluginData(BaseModel):
    name: str
    options: dict

class NewAnalysis(BaseModel):
    plugins: List[NewAnalysisPluginData]
    submission_uuid: uuid.UUID
    primary_uuid: uuid.UUID
    ignore_uuids: Union[None, List[Union[uuid.UUID, None]]]

class NewAnalysisResponse(BaseModel):
    job_uuid: uuid.UUID

# Jobs

class JobItem(BaseModel):
    _key: str
    user: str
    primary: Union[uuid.UUID, None]
    submission: SubmissionItem
    start_time: int
    complete_time: int
    complete: bool
    error: Union[List[str], None]
    plugins: Union[List[str], None]
    plugin_args: Union[dict, None]
    limit_to: List[Union[uuid.UUID, None]]
    score: float
    runner: str
    uuid: uuid.UUID

class JobItemExtended(JobItem):
    signature_count: int
    report_count: int
    exec_inst_count: int

class JobList(BaseModel):
    jobs: List[JobItem]
    total: int

# SubmissionFile

class SubmissionFileItem(BaseModel):
    mime_type: str
    unpacked_archive: bool
    exec_format: str
    exec_type: str
    exec_arch: str
    exec_bits: str
    exec_interpreter: str
    exec_packer: str
    target_os: str
    hash: str
    dropped: bool
    uuid: uuid.UUID

class SubmissionFileList(BaseModel):
    jobs: List[SubmissionFileItem]
    total: int

# Logs

class LogItem(BaseModel):
    severity: str
    log_name: str
    message: str

class LogList(BaseModel):
    logs: List[Union[LogItem, None]]
    total: int

# Reports

class ReportItem(BaseModel):
    file_uuid: Union[uuid.UUID, None]
    name: str
    value: str
    report_type: str
    uuid: str

class ReportList(BaseModel):
    reports: List[Union[ReportItem, None]]
    total: int

# Signatures

class SignatureItem(BaseModel):
    name: str
    description: str
    plugin: str
    severity: SIGNATURE_SEVERITY
    uuid: str

class SignatureMatchItem(BaseModel):
    file_uuid: Union[uuid.UUID, None]
    extra: List[Union[str, None]]
    match_time: int
    signature: SignatureItem
    uuid: uuid.UUID

class SignatureMatchList(BaseModel):
    signatures: List[Union[SignatureMatchItem, None]]
    total: int

# Metadata

class MetadataItem(BaseModel):
    key: str
    value: str
    uuid: str

class MetadataList(BaseModel):
    items: List[Union[MetadataItem, None]]
    total: int

MetadataMap = Dict[str, int]

# Process data

class ProcessEvent(BaseModel):
    key: str
    src: str
    dest: str
    data: str
    time: int
    success: bool
    uuid: str

class ProcessEventList(BaseModel):
    events: List[Union[ProcessEvent, None]]
    total: int

class SyscallList(BaseModel):
    syscalls: List[Union[dict, None]]
    total: int

class ProcessItem(BaseModel):
    pid: int
    parent_pid: int
    path: str
    command_line: str
    start_time: int
    end_time: int
    event_total: int
    child_processes: Union['List[ProcessItem]', None]
    # child_process_uuids: Union[List[Union[uuid.UUID, None]], None]
    syscall_total: int
    event_total: int
    libraries: Union[List[Union[str, None]], None]
    uuid: uuid.UUID


# ExecInstance data

class ExecInstanceItem(BaseModel):
    submission_uuid: uuid.UUID
    start_time: float
    end_time: float
    exec_module: str
    run_os: str
    screenshots: List[str]
    process_count: int
    processes: Union[None, List[Union[ProcessItem, None]]]
    uuid: uuid.UUID

class ExecInstanceList(BaseModel):
    instances: List[Union[ExecInstanceItem, None]]
    total: int   
