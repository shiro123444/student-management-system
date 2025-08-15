"""
Export and reporting endpoints
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional, List
import logging
import uuid
from datetime import datetime, timedelta
import io

from app.services.export_service import ExportService
from app.services.report_service import ReportService
from app.services.progress_service import ProgressService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
export_service = ExportService()
report_service = ReportService()
progress_service = ProgressService()

@router.post("/export/report")
async def generate_report(
    background_tasks: BackgroundTasks,
    report_type: str = Query(..., description="Type of report: usage, knowledge_gaps, performance"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    format: str = Query("json", description="Export format: json, csv, pdf"),
    include_analytics: bool = Query(True, description="Include analytics data")
):
    """
    Generate various types of reports
    """
    try:
        # Validate parameters
        valid_report_types = ["usage", "knowledge_gaps", "performance", "content_analysis"]
        if report_type not in valid_report_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type. Valid types: {valid_report_types}"
            )
        
        valid_formats = ["json", "csv", "pdf"]
        if format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Valid formats: {valid_formats}"
            )
        
        # Parse dates
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        # Generate report ID
        report_id = str(uuid.uuid4())
        
        # Start background report generation
        progress_id = await progress_service.start_task(
            task_type="report_generation",
            metadata={
                "report_id": report_id,
                "report_type": report_type,
                "format": format
            }
        )
        
        background_tasks.add_task(
            report_service.generate_report,
            report_id,
            report_type,
            start_dt,
            end_dt,
            format,
            include_analytics,
            progress_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "report_id": report_id,
                "progress_id": progress_id,
                "message": "Report generation started",
                "estimated_completion": "2-5 minutes"
            }
        )
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )

@router.get("/export/report/{report_id}")
async def download_report(report_id: str):
    """
    Download a generated report
    """
    try:
        report_data = await export_service.get_report(report_id)
        
        if not report_data:
            raise HTTPException(
                status_code=404,
                detail="Report not found or not ready"
            )
        
        # Create streaming response based on format
        if report_data["format"] == "json":
            content = report_data["content"]
            media_type = "application/json"
            filename = f"report_{report_id}.json"
        elif report_data["format"] == "csv":
            content = report_data["content"]
            media_type = "text/csv"
            filename = f"report_{report_id}.csv"
        elif report_data["format"] == "pdf":
            content = report_data["content"]
            media_type = "application/pdf"
            filename = f"report_{report_id}.pdf"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Create file-like object
        file_buffer = io.BytesIO(content.encode() if isinstance(content, str) else content)
        
        return StreamingResponse(
            io.BytesIO(file_buffer.getvalue()),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Report download failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Report download failed: {str(e)}"
        )

@router.get("/export/knowledge-graph")
async def export_knowledge_graph(
    format: str = Query("json", description="Export format: json, graphml, cypher"),
    include_embeddings: bool = Query(False, description="Include vector embeddings")
):
    """
    Export the knowledge graph
    """
    try:
        graph_data = await export_service.export_knowledge_graph(
            format=format,
            include_embeddings=include_embeddings
        )
        
        if format == "json":
            return JSONResponse(content=graph_data)
        else:
            # For other formats, return as file download
            content = graph_data["content"]
            filename = f"knowledge_graph.{format}"
            
            if format == "graphml":
                media_type = "application/xml"
            elif format == "cypher":
                media_type = "text/plain"
            else:
                media_type = "application/octet-stream"
            
            return StreamingResponse(
                io.BytesIO(content.encode()),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
    except Exception as e:
        logger.error(f"Knowledge graph export failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge graph export failed: {str(e)}"
        )

@router.get("/export/analytics")
async def export_analytics(
    metric_types: List[str] = Query([], description="Specific metrics to export"),
    aggregation_level: str = Query("daily", description="Aggregation: hourly, daily, weekly")
):
    """
    Export analytics and usage data
    """
    try:
        analytics_data = await export_service.export_analytics(
            metric_types=metric_types,
            aggregation_level=aggregation_level
        )
        
        return JSONResponse(content=analytics_data)
        
    except Exception as e:
        logger.error(f"Analytics export failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analytics export failed: {str(e)}"
        )

@router.get("/export/status/{report_id}")
async def get_export_status(report_id: str):
    """
    Get the status of an export/report generation
    """
    try:
        status = await export_service.get_export_status(report_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Export not found"
            )
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get export status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get export status: {str(e)}"
        )

@router.delete("/export/report/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a generated report
    """
    try:
        success = await export_service.delete_report(report_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        return {"message": f"Report {report_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )