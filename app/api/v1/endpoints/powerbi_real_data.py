"""
PowerBI Dashboard Endpoints - 100% REAL SQL Server Data
=======================================================

Endpoints optimizados para PowerBI que usan las tablas REALES:
- GD_R_InvestmentPosition → Posiciones reales
- GD_R_Profit_And_Lost_Investment → P&L real
- GD_R_Unit_Appraisal_Fund → NAV real  
- GD_R_TransactionHistory → Transacciones reales

Author: Investment Data Analysis Agent
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, date
from sqlalchemy import text
import structlog

from app.database.connection import DatabaseManager

router = APIRouter(prefix="/powerbi-real", tags=["PowerBI Real Data"])
logger = structlog.get_logger(__name__)


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    return db_manager


@router.get("/positions-all", summary="📋 PowerBI - All Real Positions")
async def get_all_real_positions_for_powerbi(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Posiciones REALES de TODOS los fondos desde GD_R_InvestmentPosition
    """
    try:
        query = text("""
        SELECT TOP 1000
            CAST(PshipID as INT) as PshipID,
            Portfolio as FundName,
            Fecha as AsOfDate,
            InvestDescription as AssetName,
            InvestID as AssetCode,
            Qty as Quantity,
            LocalPrice as UnitPrice,
            MVBook as MarketValue,
            LocalCurrency as Currency,
            PercentInvest as Weight,
            LSDesc as AssetCategory
        FROM GD_R_InvestmentPosition
        WHERE PshipID IN (
            SELECT PshipID FROM GD_Fondos WHERE FN_Activo = 1
        )
        AND Fecha >= '2022-01-01'
        ORDER BY PshipID, MVBook DESC
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            positions = []
            
            for row in result:
                position = {
                    "PshipID": int(row.PshipID),
                    "FundName": row.FundName,
                    "AsOfDate": row.AsOfDate.isoformat() if row.AsOfDate else None,
                    "AssetName": row.AssetName if row.AssetName else "Unknown",
                    "AssetCode": row.AssetCode if row.AssetCode else "N/A",
                    "Quantity": float(row.Quantity) if row.Quantity else 0,
                    "UnitPrice": float(row.UnitPrice) if row.UnitPrice else 0,
                    "MarketValue": float(row.MarketValue) if row.MarketValue else 0,
                    "Currency": row.Currency if row.Currency else "CLP",
                    "Weight": float(row.Weight) if row.Weight else 0,
                    "AssetCategory": row.AssetCategory if row.AssetCategory else "Other"
                }
                positions.append(position)
        
        logger.info("Posiciones REALES preparadas para PowerBI", total_positions=len(positions))
        
        return positions
        
    except Exception as e:
        logger.error("Error obteniendo posiciones reales para PowerBI", error=str(e))
        raise HTTPException(status_code=500, detail=f"Real positions error: {str(e)}")


@router.get("/pnl-all", summary="💰 PowerBI - All Real P&L")
async def get_all_real_pnl_for_powerbi(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    P&L REAL de TODOS los fondos desde GD_R_Profit_And_Lost_Investment
    """
    try:
        query = text("""
        SELECT TOP 1000
            CAST(PshipID as INT) as PshipID,
            Portfolio as FundName,
            Fecha as PLDate,
            Symb as AssetSymbol,
            Invest as AssetName,
            Group1 as AssetCategory,
            PRgain as RealizedPL,
            PUgain as UnrealizedPL,
            FxRgain as FXRealizedPL,
            FxUgain as FXUnrealizedPL,
            Income as IncomeReceived,
            TotGL as TotalPL,
            PctGL as PercentPL,
            BasisPoint as BasisPoints
        FROM GD_R_Profit_And_Lost_Investment
        WHERE PshipID IN (
            SELECT PshipID FROM GD_Fondos WHERE FN_Activo = 1
        )
        AND Fecha >= '2022-01-01'
        ORDER BY PshipID, TotGL DESC
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            pnl_data = []
            
            for row in result:
                pnl = {
                    "PshipID": int(row.PshipID),
                    "FundName": row.FundName,
                    "PLDate": row.PLDate.isoformat() if row.PLDate else None,
                    "AssetSymbol": row.AssetSymbol if row.AssetSymbol else "N/A",
                    "AssetName": row.AssetName if row.AssetName else "Unknown",
                    "AssetCategory": row.AssetCategory if row.AssetCategory else "Other",
                    "RealizedPL": float(row.RealizedPL) if row.RealizedPL else 0,
                    "UnrealizedPL": float(row.UnrealizedPL) if row.UnrealizedPL else 0,
                    "FXRealizedPL": float(row.FXRealizedPL) if row.FXRealizedPL else 0,
                    "FXUnrealizedPL": float(row.FXUnrealizedPL) if row.FXUnrealizedPL else 0,
                    "IncomeReceived": float(row.IncomeReceived) if row.IncomeReceived else 0,
                    "TotalPL": float(row.TotalPL) if row.TotalPL else 0,
                    "PercentPL": float(row.PercentPL) if row.PercentPL else 0,
                    "BasisPoints": float(row.BasisPoints) if row.BasisPoints else 0
                }
                pnl_data.append(pnl)
        
        logger.info("P&L REAL preparado para PowerBI", total_records=len(pnl_data))
        
        return pnl_data
        
    except Exception as e:
        logger.error("Error obteniendo P&L real para PowerBI", error=str(e))
        raise HTTPException(status_code=500, detail=f"Real P&L error: {str(e)}")


@router.get("/nav-all", summary="📈 PowerBI - All Real NAV")
async def get_all_real_nav_for_powerbi(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    NAV REAL de TODOS los fondos desde GD_R_Unit_Appraisal_Fund
    """
    try:
        query = text("""
        SELECT TOP 1000
            int(PshipID) as PshipID,
            Portfolio as FundName,
            Fecha as NAVDate,
            UnitsValue as NAV,
            UnitsOs as UnitsOutstanding,
            NetAssetValue as TotalNetAssets,
            BaseCurrency as Currency
        FROM GD_R_Unit_Appraisal_Fund
        WHERE PshipID IN (
            SELECT PshipID FROM GD_Fondos WHERE FN_Activo = 1
        )
        AND Fecha >= '2022-01-01'
        ORDER BY PshipID, Fecha DESC
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            nav_data = []
            
            for row in result:
                nav = {
                    "PshipID": int(row.PshipID),
                    "FundName": row.FundName,
                    "NAVDate": row.NAVDate.isoformat() if row.NAVDate else None,
                    "NAV": float(row.NAV) if row.NAV else 0,
                    "UnitsOutstanding": float(row.UnitsOutstanding) if row.UnitsOutstanding else 0,
                    "TotalNetAssets": float(row.TotalNetAssets) if row.TotalNetAssets else 0,
                    "Currency": row.Currency if row.Currency else "CLP"
                }
                nav_data.append(nav)
        
        logger.info("NAV REAL preparado para PowerBI", total_records=len(nav_data))
        
        return nav_data
        
    except Exception as e:
        logger.error("Error obteniendo NAV real para PowerBI", error=str(e))
        raise HTTPException(status_code=500, detail=f"Real NAV error: {str(e)}")


@router.get("/overview-complete", summary="🎯 PowerBI - Complete Real Overview")
async def get_complete_real_overview_for_powerbi(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Overview completo con datos REALES: fondos + últimas posiciones + último NAV
    """
    try:
        query = text("""
        SELECT 
            f.PshipID,
            f.Portfolio as FundName,
            f.FN_Activo as IsActive,
            COALESCE(latest_nav.NAV, 0) as LatestNAV,
            COALESCE(latest_nav.NAVDate, f.CreationDate) as LastNavDate,
            COALESCE(pos_summary.TotalPositions, 0) as MarketValue,
            COALESCE(pos_summary.PositionCount, 0) as HoldingsCount,
            COALESCE(pnl_summary.TotalPL, 0) as TotalPL,
            COALESCE(latest_nav.Currency, 'CLP') as Currency
        FROM GD_Fondos f
        LEFT JOIN (
            SELECT 
                PshipID,
                UnitsValue as NAV,
                Fecha as NAVDate,
                BaseCurrency as Currency,
                ROW_NUMBER() OVER (PARTITION BY PshipID ORDER BY Fecha DESC) as rn
            FROM GD_R_Unit_Appraisal_Fund
            WHERE Fecha >= '2022-01-01'
        ) latest_nav ON f.PshipID = latest_nav.PshipID AND latest_nav.rn = 1
        LEFT JOIN (
            SELECT 
                PshipID,
                SUM(MVBook) as TotalPositions,
                COUNT(*) as PositionCount
            FROM GD_R_InvestmentPosition
            WHERE Fecha >= '2022-01-01'
            GROUP BY PshipID
        ) pos_summary ON f.PshipID = pos_summary.PshipID
        LEFT JOIN (
            SELECT 
                PshipID,
                SUM(TotGL) as TotalPL
            FROM GD_R_Profit_And_Lost_Investment
            WHERE Fecha >= '2022-01-01'
            GROUP BY PshipID
        ) pnl_summary ON f.PshipID = pnl_summary.PshipID
        WHERE f.FN_Activo = 1
        ORDER BY f.PshipID
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            overview_data = []
            
            for row in result:
                overview = {
                    "PshipID": int(row.PshipID),
                    "FundName": row.FundName,
                    "IsActive": bool(row.IsActive),
                    "LatestNAV": float(row.LatestNAV) if row.LatestNAV else 0,
                    "LastNavDate": row.LastNavDate.isoformat() if row.LastNavDate else None,
                    "MarketValue": float(row.MarketValue) if row.MarketValue else 0,
                    "HoldingsCount": int(row.HoldingsCount) if row.HoldingsCount else 0,
                    "TotalPL": float(row.TotalPL) if row.TotalPL else 0,
                    "Currency": row.Currency if row.Currency else "CLP"
                }
                overview_data.append(overview)
        
        logger.info("Overview REAL completo preparado para PowerBI", total_funds=len(overview_data))
        
        return overview_data
        
    except Exception as e:
        logger.error("Error obteniendo overview real completo para PowerBI", error=str(e))
        raise HTTPException(status_code=500, detail=f"Real overview error: {str(e)}")