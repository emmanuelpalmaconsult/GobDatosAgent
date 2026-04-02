"""
Health and system status endpoints
Provides system health checks, database status, and monitoring endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import structlog
from datetime import datetime

from app.models.schemas import BaseResponse, DatabaseStatus, TableStatus
from app.database.connection import DatabaseManager
from app.core.config import settings, db_settings

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=BaseResponse)
async def health_check():
    """
    Basic health check endpoint
    Returns system status and basic information
    """
    try:
        # Test database connection
        db_manager = DatabaseManager()
        await db_manager.connect()
        db_status = await db_manager.test_connections()
        
        is_healthy = db_status.get("source", False)
        
        return BaseResponse(
            success=True,
            message=f"Investment Data Analysis Agent is {'healthy' if is_healthy else 'unhealthy'}",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return BaseResponse(
            success=False,
            message=f"Health check failed: {str(e)}",
            timestamp=datetime.utcnow()
        )


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """
    Detailed health check with system information
    """
    try:
        db_manager = DatabaseManager()
        
        # Test database connection
        db_connected = await db_manager.test_connection()
        
        # Get database statistics if connected
        db_stats = {}
        if db_connected:
            db_stats = await db_manager.get_database_stats()
        
        # Check external integrations
        integrations = {
            "powerbi": settings.powerbi_configured,
            "google_datastudio": settings.google_configured,
            "openai": settings.openai_configured
        }
        
        return {
            "status": "healthy" if db_connected else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": {
                "connected": db_connected,
                "name": settings.SQL_SERVER_DATABASE,
                "host": settings.SQL_SERVER_HOST,
                **db_stats
            },
            "integrations": integrations,
            "system": {
                "debug_mode": settings.DEBUG,
                "api_prefix": settings.API_PREFIX,
                "cors_enabled": len(settings.CORS_ORIGINS) > 0
            }
        }
        
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/database", response_model=DatabaseStatus)            
async def database_status():
    """
    Comprehensive database status and table information
    """
    try:
        db_manager = DatabaseManager()
        
        # Test connection
        await db_manager.connect()
        connection_status = await db_manager.test_connections()
        is_connected = connection_status.get("source", False)
        
        if not is_connected:
            return DatabaseStatus(
                success=False,
                message="Database connection failed",
                connection_status="disconnected",
                total_tables=0,
                active_tables=0,
                table_details=[]
            )
        
        # Get available tables
        available_tables = await db_manager.get_available_tables()
        active_tables = await db_manager.get_active_tables()
        
        # Get detailed table information
        table_details = []
        for table_name in available_tables:
            try:
                # Check if table is in our configured tables
                is_configured_table = table_name in (
                    db_settings.core_tables + 
                    db_settings.analysis_tables + 
                    db_settings.control_tables
                )
                
                if is_configured_table:
                    schema = await db_manager.get_table_schema(table_name)
                    table_details.append(TableStatus(
                        table_name=table_name,
                        is_active=db_manager.is_table_active(table_name),
                        record_count=schema.get("row_count", 0),
                        last_updated=datetime.utcnow(),
                        analysis_priority=1 if table_name in db_settings.core_tables else 2
                    ))
            except Exception as e:
                logger.warning("Failed to get table details", table=table_name, error=str(e))
        
        return DatabaseStatus(
            success=True,
            message="Database status retrieved successfully",
            connection_status="connected",
            total_tables=len(available_tables),
            active_tables=len(active_tables),
            table_details=table_details,
            last_analysis=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Database status check failed", error=str(e))
        return DatabaseStatus(
            success=False,
            message=f"Database status check failed: {str(e)}",
            connection_status="error",
            total_tables=0,
            active_tables=0,
            table_details=[]
        )


@router.get("/tables/{table_name}")
async def table_health_check(table_name: str):
    """
    Health check for a specific table
    """
    try:
        db_manager = DatabaseManager()
        
        # Check if table exists and is accessible
        available_tables = await db_manager.get_available_tables()
        
        if table_name not in available_tables:
            raise HTTPException(
                status_code=404, 
                detail=f"Table '{table_name}' not found"
            )
        
        # Get table schema and basic stats
        schema = await db_manager.get_table_schema(table_name)
        
        # Check if table is active
        is_active = db_manager.is_table_active(table_name)
        
        # Get sample data
        sample_data = await db_manager.get_table_data(table_name, limit=5)
        
        return {
            "table_name": table_name,
            "status": "healthy",
            "is_active": is_active,
            "record_count": schema.get("row_count", 0),
            "column_count": len(schema.get("columns", [])),
            "sample_records": len(sample_data),
            "schema": schema,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Table health check failed", table=table_name, error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Table health check failed: {str(e)}"
        )


@router.post("/tables/{table_name}/toggle")
async def toggle_table_status(table_name: str):
    """
    Toggle table active/inactive status for analysis
    """
    try:
        db_manager = DatabaseManager()
        
        # Check if table exists
        available_tables = await db_manager.get_available_tables()
        
        if table_name not in available_tables:
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get current status and toggle
        current_status = db_manager.is_table_active(table_name)
        new_status = not current_status
        
        # Update status
        await db_manager.set_table_active(table_name, new_status)
        
        logger.info(
            "Table status toggled", 
            table=table_name, 
            old_status=current_status, 
            new_status=new_status
        )
        
        return {
            "table_name": table_name,
            "previous_status": "active" if current_status else "inactive",
            "new_status": "active" if new_status else "inactive",
            "message": f"Table '{table_name}' is now {'active' if new_status else 'inactive'}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to toggle table status", table=table_name, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to toggle table status: {str(e)}"
        )