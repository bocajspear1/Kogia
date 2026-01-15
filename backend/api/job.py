import uuid

from fastapi import APIRouter, Request, HTTPException

from .types import OptionalStrParam, JobList, JobItem, OptionalFlagParam, SubmissionItem, \
    JobItemExtended, LogList, LogItem, ReportItem, ReportList, SignatureItem, SignatureMatchList, SignatureMatchItem, \
    ExecInstanceItem, ExecInstanceList, JobExportData, JobExportResponse

from typing_extensions import Annotated, List, Union

from fastapi import Form, File, UploadFile, Query
from fastapi.responses import Response


from backend.lib.job import Job
from backend.lib.helpers import generate_download_token

#
# Job API endpoints
#
router = APIRouter(tags=['job'])

@router.get('/list')
def get_job_list(req : Request, submission_uuid : OptionalStrParam = None, skip=0, limit=30):
    with req.app._db.lock:

        if submission_uuid is not None:
            if submission_uuid != "":
                print(submission_uuid)
                try:
                    uuid.UUID(submission_uuid)
                except ValueError:
                    raise HTTPException(400, "Invalid UUID")
            elif submission_uuid.strip() == "":
                submission_uuid = None

            
        job_list = []
        total_len = 0
        
        if submission_uuid is None:
            total_len, job_list = Job.list_dict(req.app._db, skip=skip, limit=limit)
        else:
            total_len, job_list = Job.list_dict(req.app._db, skip=skip, limit=limit, submission_uuid=submission_uuid)

    item_list = []
    for job in job_list:
        submission = SubmissionItem(**job['submission'])
        job['submission'] = submission
        print(job)
        item_list.append(JobItem(**job))

    return JobList(jobs=item_list, total=total_len)

@router.get('/{uuid}/info')
def get_job_info(req : Request, uuid : uuid.UUID):
    with req.app._db.lock:
        job = Job(req.app._db, req.app._filestore, uuid=uuid)
        job.load(req.app._manager)
        if not job.found:
            raise HTTPException(404, "Job not found")
    
        resp = job.to_dict(full_dict=True)

        submission = SubmissionItem(**resp['submission'])
        resp['submission'] = submission
        
        signature_list = job.get_signatures()
        resp['signature_count'] = len(signature_list)
        reports_count, _ = job.get_reports()
        resp['report_count'] = reports_count
        exec_inst_count, _ = job.get_exec_instances()
        resp['exec_inst_count'] = exec_inst_count

    return JobItemExtended(**resp)

@router.get('/{uuid}/logs')
def get_job_logs(req : Request, uuid : uuid.UUID, skip : int=0, limit : int=30):
    
    with req.app._db.lock:
        job = Job(req.app._db, req.app._filestore, uuid=uuid)
        job.load(req.app._manager)
        if not job.found:
            
            raise HTTPException(404, "Job not found")

        log_count, log_list = job.get_logs(skip=skip, limit=limit)

    ret_list = []
    for item in log_list:
        ret_list.append(LogItem(**item))

    return LogList(logs=ret_list, total=log_count)

@router.get('/{uuid}/reports')
def get_job_reports(req : Request, uuid : uuid.UUID, file : OptionalStrParam = None, skip : int=0, limit : int=30) -> ReportList:
    with req.app._db.lock:
        job = Job(req.app._db, req.app._filestore, uuid=uuid)
        job.load(req.app._manager)
        if not job.found:
            raise HTTPException(404, "Job not found")

        report_count, reports = job.get_reports(file_uuid=file, skip=skip, limit=limit)


    report_list = []
    for report in reports:
        report_list.append(ReportItem(**report))
    return ReportList(reports=report_list, total=report_count)

@router.get('/{uuid}/signatures')
def get_job_signatures(req : Request, uuid : uuid.UUID, file_uuid : OptionalStrParam = None) -> SignatureMatchList:
    with req.app._db.lock:
        job = Job(req.app._db, req.app._filestore, uuid=uuid)
        job.load(req.app._manager)
        job.load_matches()
        if not job.found:
            raise HTTPException(404, "Job not found")
        matches = job.get_matches(file_uuid=file_uuid)

        signature_list = []
        for match_item in matches:
            dict_item = match_item.to_dict(full=True)
            signature_list.append(SignatureMatchItem(**dict_item, uuid=dict_item['_key']))


    return SignatureMatchList(signatures=signature_list, total=0)

@router.get('/{uuid}/exec_instances')
def get_job_exec_instances(req : Request, uuid : uuid.UUID):

    with req.app._db.lock:
        job = Job(req.app._db, req.app._filestore, uuid=uuid)
        job.load(req.app._manager)
        if not job.found:
            raise HTTPException(404, "Job not found")
        inst_count, inst_list = job.get_exec_instances()

    ret_list = []

    for inst in inst_list:
        ret_list.append(ExecInstanceItem(**inst.to_dict()))

    return ExecInstanceList(instances=ret_list, total=inst_count)

# @job_endpoints.route('/<uuid>/details', methods=['GET'])
# def get_job_details(uuid):
#     current_app._db.lock()
#     job = Job(current_app._db, current_app._filestore, uuid=uuid)
#     job.load(current_app._manager)
#     if job.uuid == None:
#         return abort(404)
#     plugin_details = job.plugins

#     job_data = {
#         "plugins": plugin_details
#     }

#     current_app._db.unlock()

#     return jsonify({
#         "ok": True,
#         "result": job_data
#     })


@router.post('/{job_uuid}/export/{plugin_name}')
def get_job_export_plugin(req : Request, job_uuid : uuid.UUID, plugin_name: str, export_item: JobExportData) -> JobExportResponse:

    with req.app._db.lock:

        # Load the job
        job = Job(req.app._db, req.app._filestore, uuid=job_uuid)
        job.load(req.app._manager)
        job.load_matches()
        if not job.found:
            raise HTTPException(404, "Job not found")
        
        
        # Load the plugin
        plugin = req.app._manager.get_plugin(plugin_name)
        if plugin is None:
            raise HTTPException(404, "Plugin not found")
        
        plugin_args = {}
        if export_item.export_items.options is not None:
            plugin_args = export_item.export_items.options
            # Init plugin
            init_plugin = plugin(req.app._manager, args=plugin_args)
            # current_app._manager.initialize_plugins([])[0]

            export_name, export_type = init_plugin.get_export_metadata()

            new_export = job.generate_export_file(export_name, plugin_name, export_type, req.app.req_username)

            new_export.set_event_filter(export_item.export_items.events)
            new_export.set_file_filter(export_item.export_items.files)
            new_export.set_network_filter(export_item.export_items.network)

            # Run plugin
            export_ok, export_data = init_plugin.export(job, new_export)


        if export_ok == True:
            # Save file to filestore
            file_io = new_export.create_file()
            file_io.write(export_data)
            new_export.close_file()

            new_export.save()

            new_token = generate_download_token(req.app, new_export.uuid)
            return JobExportResponse(download_token=new_token, export_uuid=new_export.uuid)

        else:
            raise HTTPException(500, "Export plugin failed: " + export_ok)
            return json_resp_invalid()


# @job_endpoints.route('/<uuid>/export/<export_uuid>', methods=['POST'])
# def get_job_export_file(uuid, plugin_name):