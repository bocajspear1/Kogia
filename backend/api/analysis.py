"""Analysis endpoints (/analysis)

"""
import uuid

from backend.lib.submission import Submission
from backend.lib.job import Job

from fastapi import APIRouter, Request, HTTPException

from typing_extensions import Annotated, List, Union

from fastapi import Form, File, UploadFile, Query
from fastapi.responses import Response
from .types import NewAnalysisResponse, NewAnalysis

router = APIRouter(tags=['analysis'])

#
# Analysis API endpoints
#

@router.post('/new')
def create_analysis_job(req : Request, new_analysis : NewAnalysis) -> NewAnalysisResponse:


    req.app._db.lock()

    submission = Submission(uuid=str(new_analysis.submission_uuid))
    submission.load(req.app._db)

    new_job = Job.new(submission, str(new_analysis.primary_uuid), req.app._db_factory.new(), req.app._filestore)

    for plugin in new_analysis.plugins:
        
        add_plugin_class = req.app._manager.get_plugin(plugin.name)
        
        add_plugin = None
        if plugin.options is not None and len(plugin.options) > 0:
            new_job.add_plugin(add_plugin_class, args=plugin.options)
        else:
            new_job.add_plugin(add_plugin_class)
    
    if new_analysis.ignore_uuids is not None and len(new_analysis.ignore_uuids) > 0:
        limit_list = []
        for submission_file in submission.files:
            if submission_file.uuid not in new_analysis.ignore_uuids:
                new_job.add_limit_to_file(str(submission_file.uuid))

        
    new_job.save()
    req.app._db.unlock()

    req.app._worker_manager.assign_job(str(new_job.uuid))

    response = NewAnalysisResponse(job_uuid=str(new_job.uuid))

    return response
