"""
Investment Data Analysis Agent - SQL Server Direct Endpoints
============================================================

Endpoints que conectan directamente a las tablas REALES de SQL Server:
- GD_Fondos (PshipID, fund names, etc.)
- GD_Posiciones (positions data)
- GD_Cashflow (cash movements) 
- GD_PLL (P&L data)

Author: Investment Data Analysis Agent
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy import text
import structlog
import pandas as pd

from app.database.connection import DatabaseManager

router = APIRouter(prefix="/sqlserver", tags=["SQL Server Direct"])
logger = structlog.get_logger(__name__)


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    return db_manager


@router.get("/fondos", summary="Get real funds from GD_Fondos table")
async def get_fondos_reales(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Obtener fondos REALES desde la tabla GD_Fondos de SQL Server
    """
    try:
        query = text("""
        SELECT 
            PshipID, 
            Portfolio as fund_name,
            FN_Activo as is_active
        FROM GD_Fondos
        ORDER BY PshipID
        """)
        
        # Execute query using source database session
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            columns = result.keys()
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            fondos = []
            for row in rows:
                fondo = dict(zip(columns, row))
                fondos.append(fondo)
        
        logger.info("Fondos reales obtenidos", count=len(fondos))
        
        return {
            "total_fondos": len(fondos),
            "source_table": "GD_Fondos", 
            "fondos": fondos
        }
        
    except Exception as e:
        logger.error("Error obteniendo fondos reales", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/posiciones/{pship_id}", summary="Get real positions from GD_Posiciones")
async def get_posiciones_reales(
    pship_id: int,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Obtener posiciones REALES desde GD_Posiciones para un fondo específico
    """
    try:
        query = text("""
        SELECT 
            PshipID,
            AssetCode,
            AssetName,
            Quantity,
            MarketValue,
            Currency,
            AsOfDate
        FROM GD_Posiciones 
        WHERE PshipID = :pship_id
        ORDER BY MarketValue DESC
        """)
        
        params = {"pship_id": pship_id}
        
        with db_manager.get_source_session() as session:
            result = session.execute(query, params)
            columns = result.keys()
            rows = result.fetchall()
            
            posiciones = []
            for row in rows:
                posicion = dict(zip(columns, row))
                posiciones.append(posicion)
        
        logger.info("Posiciones reales obtenidas", pship_id=pship_id, count=len(posiciones))
        
        return {
            "PshipID": pship_id,
            "total_posiciones": len(posiciones),
            "source_table": "GD_Posiciones",
            "posiciones": posiciones
        }
        
    except Exception as e:
        logger.error("Error obteniendo posiciones reales", pship_id=pship_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/cashflow/{pship_id}", summary="Get real cashflow from GD_Cashflow")
async def get_cashflow_real(
    pship_id: int,
    limit: int = Query(100, le=1000),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Obtener cash flows REALES desde GD_Cashflow para un fondo específico
    """
    try:
        query = text("""
        SELECT TOP (:limit)
            PshipID,
            FlowDate,
            FlowType,
            Amount,
            Currency,
            Description
        FROM GD_Cashflow 
        WHERE PshipID = :pship_id
        ORDER BY FlowDate DESC
        """)
        
        params = {"pship_id": pship_id, "limit": limit}
        
        with db_manager.get_source_session() as session:
            result = session.execute(query, params)
            columns = result.keys()
            rows = result.fetchall()
            
            cashflows = []
            for row in rows:
                cashflow = dict(zip(columns, row))
                # Convert dates to string for JSON serialization
                if 'FlowDate' in cashflow and cashflow['FlowDate']:
                    cashflow['FlowDate'] = cashflow['FlowDate'].isoformat()
                cashflows.append(cashflow)
        
        logger.info("Cashflows reales obtenidos", pship_id=pship_id, count=len(cashflows))
        
        return {
            "PshipID": pship_id,
            "total_cashflows": len(cashflows),
            "source_table": "GD_Cashflow",
            "cashflows": cashflows
        }
        
    except Exception as e:
        logger.error("Error obteniendo cashflows reales", pship_id=pship_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/pll/{pship_id}", summary="Get real P&L from GD_PLL") 
async def get_pll_real(
    pship_id: int,
    limit: int = Query(50, le=500),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Obtener P&L REAL desde GD_PLL para un fondo específico
    """
    try:
        query = text("""
        SELECT TOP (:limit)
            PshipID,
            PLLDate,
            RealizedPL,
            UnrealizedPL,
            TotalPL,
            Currency,
            AsOfDate
        FROM GD_PLL 
        WHERE PshipID = :pship_id
        ORDER BY PLLDate DESC
        """)
        
        params = {"pship_id": pship_id, "limit": limit}
        
        with db_manager.get_source_session() as session:
            result = session.execute(query, params)
            columns = result.keys()
            rows = result.fetchall()
            
            pll_data = []
            for row in rows:
                pll = dict(zip(columns, row))
                # Convert dates to string for JSON serialization
                for date_field in ['PLLDate', 'AsOfDate']:
                    if date_field in pll and pll[date_field]:
                        pll[date_field] = pll[date_field].isoformat()
                pll_data.append(pll)
        
        logger.info("P&L real obtenido", pship_id=pship_id, count=len(pll_data))
        
        return {
            "PshipID": pship_id,
            "total_records": len(pll_data),
            "source_table": "GD_PLL",
            "pll_data": pll_data
        }
        
    except Exception as e:
        logger.error("Error obteniendo P&L real", pship_id=pship_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/overview", summary="Complete fund overview with real data")
async def get_overview_real(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Vista general combinando datos REALES de todas las tablas SQL Server
    """
    try:
        # Get basic fund info
        fondos_query = text("""
        SELECT 
            PshipID, 
            Portfolio as fund_name,
            FN_Activo as is_active
        FROM GD_Fondos
        WHERE FN_Activo = 1
        ORDER BY PshipID
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(fondos_query)
            columns = result.keys()
            rows = result.fetchall()
            
            fondos = []
            for row in rows:
                fondo = dict(zip(columns, row))
                fondos.append(fondo)
        
        # Get total positions value for each fund
        for fondo in fondos:
            pship_id = fondo['PshipID']
            
            # Get total positions value
            positions_query = text("""
            SELECT 
                COALESCE(SUM(MarketValue), 0) as total_positions_value,
                COUNT(*) as position_count
            FROM GD_Posiciones 
            WHERE PshipID = :pship_id
            """)
            
            with db_manager.get_source_session() as session:
                result = session.execute(positions_query, {"pship_id": pship_id})
                pos_row = result.fetchone()
                
                fondo['total_positions_value'] = float(pos_row[0]) if pos_row[0] else 0
                fondo['position_count'] = int(pos_row[1]) if pos_row[1] else 0
        
        logger.info("Overview real generado", fondos_count=len(fondos))
        
        return {
            "total_fondos_activos": len(fondos),
            "source_tables": ["GD_Fondos", "GD_Posiciones"],
            "timestamp": datetime.utcnow().isoformat(),
            "fondos": fondos
        }
        
    except Exception as e:
        logger.error("Error generando overview real", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")