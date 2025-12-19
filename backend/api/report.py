from backend.lib.data import Report

from fastapi import APIRouter, Request, HTTPException

from .types import ReportItem

router = APIRouter(tags=['report'])
#
# Report API endpoints
#

@router.get('/{uuid}')
def get_report(req : Request, uuid : str) -> ReportItem:
    req.app._db.lock()
    report = Report(uuid=uuid)
    report.load(req.app._db)
    req.app._db.unlock()
    if not report.found:
        raise HTTPException(404, detail="Report not found")

    return ReportItem(**report.to_dict())
