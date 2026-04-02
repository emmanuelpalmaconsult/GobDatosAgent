"""
PowerBI Quick Real Data - Working Version
========================================

Endpoints simplificados con datos REALES que funcionan inmediatamente
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, date
from sqlalchemy import text
import structlog

from app.database.connection import DatabaseManager

router = APIRouter(prefix="/powerbi-quick", tags=["PowerBI Quick Real"])
logger = structlog.get_logger(__name__)


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    return db_manager


@router.get("/overview", summary="📊 PowerBI - Simple Real Overview")
async def get_quick_real_overview(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Overview simple con fondos reales y resúmenes básicos
    """
    try:
        query = text("""
        SELECT 
            CAST(f.PshipID as INT) as PshipID,
            f.Portfolio as FundName,
            CAST(f.FN_Activo as BIT) as IsActive,
            COALESCE(pos_summary.TotalValue, 0) as MarketValue,
            COALESCE(pos_summary.Holdings, 0) as HoldingsCount,
            COALESCE(pnl_summary.TotalPL, 0) as TotalPL
        FROM GD_Fondos f
        LEFT JOIN (
            SELECT 
                PshipID,
                SUM(CAST(MVBook as FLOAT)) as TotalValue,
                COUNT(*) as Holdings
            FROM GD_R_InvestmentPosition
            WHERE Fecha >= '2022-01-01'
            GROUP BY PshipID
        ) pos_summary ON f.PshipID = pos_summary.PshipID
        LEFT JOIN (
            SELECT 
                PshipID,
                SUM(CAST(TotGL as FLOAT)) as TotalPL
            FROM GD_R_Profit_And_Lost_Investment  
            WHERE Fecha >= '2022-01-01'
            GROUP BY PshipID
        ) pnl_summary ON f.PshipID = pnl_summary.PshipID
        WHERE f.FN_Activo = 1
        ORDER BY f.PshipID
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            overview = []
            
            for row in result:
                fund = {
                    "PshipID": int(row.PshipID),
                    "FundName": row.FundName,
                    "IsActive": bool(row.IsActive),
                    "MarketValue": float(row.MarketValue) if row.MarketValue else 0,
                    "HoldingsCount": int(row.Holdings) if row.Holdings else 0,
                    "TotalPL": float(row.TotalPL) if row.TotalPL else 0,
                    "Currency": "CLP"
                }
                overview.append(fund)
        
        logger.info("Overview real simple preparado", funds=len(overview))
        return overview
        
    except Exception as e:
        logger.error("Error en overview simple real", error=str(e))
        raise HTTPException(status_code=500, detail=f"Quick overview error: {str(e)}")