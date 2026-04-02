"""
Dashboard PowerBI con Drill-Down para Investment Data Analysis Agent
Endpoints optimizados para consumo directo desde PowerBI
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from app.core.config import settings
import urllib.parse
from pydantic import BaseModel

# Crear router para dashboard
dashboard_router = APIRouter(prefix="/dashboard", tags=["PowerBI Dashboard"])

def get_sql_server_engine():
    """Crear conexión a SQL Server"""
    password = urllib.parse.quote_plus(settings.SOURCE_DB_PASSWORD)
    connection_string = (
        f"mssql+pyodbc://{settings.SOURCE_DB_USER}:{password}@"
        f"{settings.SOURCE_DB_HOST}:{settings.SOURCE_DB_PORT}/"
        f"{settings.SOURCE_DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&"
        f"Encrypt=yes&TrustServerCertificate=yes"
    )
    return create_engine(connection_string)

# ============================================================================
# MODELOS DE DATOS PARA POWERBI
# ============================================================================

class FundOverview(BaseModel):
    """Modelo para vista general de fondos"""
    fund_id: int
    fund_name: str
    total_assets: float
    ytd_return: float
    nav: float
    sharpe_ratio: float
    max_drawdown: float
    position_count: int
    last_update: date
    risk_level: str
    asset_class: str

class FundDetail(BaseModel):
    """Modelo para detalle de fondo específico"""
    fund_id: int
    fund_name: str
    date: date
    nav: float
    total_assets: float
    ytd_return: float
    period_irr: float
    shares: float
    currency: str
    unrealized_pnl: float
    
class PositionDetail(BaseModel):
    """Modelo para detalle de posiciones"""
    fund_id: int
    fund_name: str
    position_id: str
    instrument_name: str
    asset_class: str
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    weight_percent: float
    currency: str
    date: date

# ============================================================================
# NIVEL 1: VISTA GENERAL - TODOS LOS FONDOS
# ============================================================================

@dashboard_router.get("/overview", response_model=List[FundOverview])
async def get_funds_overview(
    date_filter: Optional[str] = Query("2026-03-31", description="Fecha de corte (YYYY-MM-DD)"),
    risk_level: Optional[str] = Query(None, description="Filtro por nivel de riesgo: low, medium, high")
):
    """
    NIVEL 1 DRILL-DOWN: Vista general de todos los fondos activos
    Optimizado para tiles y gráficos principales en PowerBI
    """
    try:
        engine = get_sql_server_engine()
        
        # Query optimizada para vista general
        query = f"""
        WITH FundPerformance AS (
            SELECT 
                f.PshipID,
                f.Portfolio as FundName,
                u.NAV,
                u.NetEndCap as TotalAssets,
                u.YTDTWR,
                u.PeriodIRR,
                u.Shares,
                u.ReportingCurrencyCode as Currency,
                u.Fecha,
                ROW_NUMBER() OVER (PARTITION BY f.PshipID ORDER BY u.Fecha DESC) as rn
            FROM [GD_EG_001].[dbo].[GD_Fondos] f
            LEFT JOIN [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u 
                ON f.PshipID = u.PshipID 
                AND u.Fecha = CAST('{date_filter}' AS DATE)
            WHERE f.FN_Activo = 1
        ),
        PositionCounts AS (
            SELECT 
                p.PshipID,
                COUNT(*) as PositionCount,
                SUM(ABS(p.UnRealGL)) as TotalUnrealizedPnL
            FROM [GD_EG_001].[dbo].[GD_R_InvestmentPosition] p
            WHERE p.Fecha = CAST('{date_filter}' AS DATE)
            AND ABS(p.MVBook) > 1000
            GROUP BY p.PshipID
        )
        SELECT 
            fp.PshipID,
            fp.FundName,
            ISNULL(fp.TotalAssets, 0) as TotalAssets,
            ISNULL(fp.YTDTWR, 0) as YTDReturn,
            ISNULL(fp.NAV, 0) as NAV,
            fp.Currency,
            ISNULL(pc.PositionCount, 0) as PositionCount,
            ISNULL(pc.TotalUnrealizedPnL, 0) as UnrealizedPnL,
            fp.Fecha as LastUpdate,
            -- Clasificación de riesgo basada en assets
            CASE 
                WHEN fp.TotalAssets > 100000000000 THEN 'Large Cap'
                WHEN fp.TotalAssets > 10000000000 THEN 'Mid Cap'  
                WHEN fp.TotalAssets > 1000000000 THEN 'Small Cap'
                ELSE 'Micro Cap'
            END as AssetClass,
            -- Nivel de riesgo estimado
            CASE 
                WHEN ABS(fp.YTDTWR) < 0.05 THEN 'Low'
                WHEN ABS(fp.YTDTWR) < 0.15 THEN 'Medium'
                ELSE 'High'
            END as RiskLevel
        FROM FundPerformance fp
        LEFT JOIN PositionCounts pc ON fp.PshipID = pc.PshipID
        WHERE fp.rn = 1
        ORDER BY fp.TotalAssets DESC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return []
        
        # Convertir a modelo PowerBI
        overview_data = []
        for _, row in df.iterrows():
            overview_data.append(FundOverview(
                fund_id=int(row['PshipID']),
                fund_name=row['FundName'],
                total_assets=float(row['TotalAssets']) if pd.notna(row['TotalAssets']) else 0.0,
                ytd_return=float(row['YTDReturn']) if pd.notna(row['YTDReturn']) else 0.0,
                nav=float(row['NAV']) if pd.notna(row['NAV']) else 0.0,
                sharpe_ratio=0.0,  # Calculado en tiempo real si es necesario
                max_drawdown=0.0,    # Calculado en tiempo real si es necesario
                position_count=int(row['PositionCount']) if pd.notna(row['PositionCount']) else 0,
                last_update=row['LastUpdate'] if pd.notna(row['LastUpdate']) else date.today(),
                risk_level=row['RiskLevel'],
                asset_class=row['AssetClass']
            ))
        
        # Filtrar por risk level si se especifica
        if risk_level:
            overview_data = [fund for fund in overview_data if fund.risk_level.lower() == risk_level.lower()]
        
        return overview_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fund overview: {str(e)}")

# ============================================================================
# NIVEL 2: DETALLE DE FONDO ESPECÍFICO
# ============================================================================

@dashboard_router.get("/fund/{fund_id}", response_model=List[FundDetail])
async def get_fund_details(
    fund_id: int,
    start_date: Optional[str] = Query("2025-01-01", description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query("2026-03-31", description="Fecha fin (YYYY-MM-DD)")
):
    """
    NIVEL 2 DRILL-DOWN: Historia detallada de un fondo específico
    Permite gráficos de tiempo y análisis de performance
    """
    try:
        engine = get_sql_server_engine()
        
        query = f"""
        SELECT 
            u.PshipID,
            u.Portfolio as FundName,
            u.Fecha,
            u.NAV,
            u.NetEndCap as TotalAssets,
            u.YTDTWR as YTDReturn,
            u.PeriodIRR,
            u.Shares,
            u.ReportingCurrencyCode as Currency,
            u.BegCapChanges,
            u.EndCapChanges,
            (u.EndCapChanges - u.BegCapChanges) as UnrealizedPnL
        FROM [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u
        WHERE u.PshipID = {fund_id}
        AND u.Fecha BETWEEN CAST('{start_date}' AS DATE) AND CAST('{end_date}' AS DATE)
        ORDER BY u.Fecha DESC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for fund {fund_id}")
        
        # Convertir a modelo PowerBI
        details = []
        for _, row in df.iterrows():
            details.append(FundDetail(
                fund_id=int(row['PshipID']),
                fund_name=row['FundName'],
                date=row['Fecha'],
                nav=float(row['NAV']) if pd.notna(row['NAV']) else 0.0,
                total_assets=float(row['TotalAssets']) if pd.notna(row['TotalAssets']) else 0.0,
                ytd_return=float(row['YTDReturn']) if pd.notna(row['YTDReturn']) else 0.0,
                period_irr=float(row['PeriodIRR']) if pd.notna(row['PeriodIRR']) else 0.0,
                shares=float(row['Shares']) if pd.notna(row['Shares']) else 0.0,
                currency=row['Currency'] if pd.notna(row['Currency']) else 'USD',
                unrealized_pnl=float(row['UnrealizedPnL']) if pd.notna(row['UnrealizedPnL']) else 0.0
            ))
        
        return details
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fund details: {str(e)}")

# ============================================================================
# NIVEL 3: POSICIONES POR ASSET CLASS
# ============================================================================

@dashboard_router.get("/fund/{fund_id}/positions", response_model=List[PositionDetail])
async def get_fund_positions(
    fund_id: int,
    date_filter: Optional[str] = Query("2026-03-31", description="Fecha de corte (YYYY-MM-DD)"),
    asset_class: Optional[str] = Query(None, description="Filtro por clase de activo"),
    min_weight: Optional[float] = Query(0.01, description="Peso mínimo (1% = 0.01)")
):
    """
    NIVEL 3 DRILL-DOWN: Posiciones detalladas de un fondo
    Permite análisis por asset class y peso
    """
    try:
        engine = get_sql_server_engine()
        
        query = f"""
        SELECT 
            p.PshipID,
            p.Portfolio as FundName,
            p.LSDesc as InstrumentName,
            p.InvestID,
            p.ReportMode as AssetClass,
            p.MVBook as MarketValue,
            p.CostBook as CostBasis,
            p.UnRealGL as UnrealizedPnL,
            p.PercentInvest as WeightPercent,
            p.Fecha,
            -- Crear ID único para posición
            CAST(p.PshipID AS VARCHAR) + '_' + p.InvestID + '_' + CAST(p.IP_IDREG AS VARCHAR) as PositionId
        FROM [GD_EG_001].[dbo].[GD_R_InvestmentPosition] p
        WHERE p.PshipID = {fund_id}
        AND p.Fecha = CAST('{date_filter}' AS DATE)
        AND ABS(p.MVBook) > 1000
        AND ABS(p.PercentInvest) >= {min_weight * 100}  -- PercentInvest está en porcentaje
        ORDER BY ABS(p.MVBook) DESC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return []
        
        # Filtrar por asset class si se especifica
        if asset_class:
            df = df[df['AssetClass'].str.contains(asset_class, case=False, na=False)]
        
        # Convertir a modelo PowerBI
        positions = []
        for _, row in df.iterrows():
            positions.append(PositionDetail(
                fund_id=int(row['PshipID']),
                fund_name=row['FundName'],
                position_id=row['PositionId'],
                instrument_name=row['InstrumentName'],
                asset_class=row['AssetClass'] if pd.notna(row['AssetClass']) else 'Unknown',
                market_value=float(row['MarketValue']) if pd.notna(row['MarketValue']) else 0.0,
                cost_basis=float(row['CostBasis']) if pd.notna(row['CostBasis']) else 0.0,
                unrealized_pnl=float(row['UnrealizedPnL']) if pd.notna(row['UnrealizedPnL']) else 0.0,
                weight_percent=float(row['WeightPercent']) if pd.notna(row['WeightPercent']) else 0.0,
                currency=row['InvestID'] if pd.notna(row['InvestID']) else 'USD',
                date=row['Fecha']
            ))
        
        return positions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fund positions: {str(e)}")

# ============================================================================
# NIVEL 4: KPIs AGREGADOS PARA CHARTS
# ============================================================================

@dashboard_router.get("/kpis/summary")
async def get_summary_kpis(
    date_filter: Optional[str] = Query("2026-03-31", description="Fecha de corte (YYYY-MM-DD)")
):
    """
    KPIs principales para dashboard PowerBI - Cards y métricas principales
    """
    try:
        engine = get_sql_server_engine()
        
        query = f"""
        WITH FundSummary AS (
            SELECT 
                COUNT(DISTINCT f.PshipID) as TotalFunds,
                SUM(ISNULL(u.NetEndCap, 0)) as TotalAUM,
                AVG(ISNULL(u.YTDTWR, 0)) as AvgYTDReturn,
                MAX(ISNULL(u.YTDTWR, 0)) as BestYTDReturn,
                MIN(ISNULL(u.YTDTWR, 0)) as WorstYTDReturn,
                AVG(ISNULL(u.NAV, 0)) as AvgNAV
            FROM [GD_EG_001].[dbo].[GD_Fondos] f
            LEFT JOIN [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u 
                ON f.PshipID = u.PshipID 
                AND u.Fecha = CAST('{date_filter}' AS DATE)
            WHERE f.FN_Activo = 1
        ),
        PositionSummary AS (
            SELECT 
                COUNT(*) as TotalPositions,
                COUNT(DISTINCT p.PshipID) as FundsWithPositions,
                SUM(ABS(p.UnRealGL)) as TotalUnrealizedPnL
            FROM [GD_EG_001].[dbo].[GD_R_InvestmentPosition] p
            WHERE p.Fecha = CAST('{date_filter}' AS DATE)
            AND ABS(p.MVBook) > 1000
        )
        SELECT *
        FROM FundSummary, PositionSummary
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return {"error": "No data available"}
        
        row = df.iloc[0]
        
        return {
            "total_funds": int(row['TotalFunds']) if pd.notna(row['TotalFunds']) else 0,
            "total_aum": float(row['TotalAUM']) if pd.notna(row['TotalAUM']) else 0.0,
            "avg_ytd_return": float(row['AvgYTDReturn']) if pd.notna(row['AvgYTDReturn']) else 0.0,
            "best_ytd_return": float(row['BestYTDReturn']) if pd.notna(row['BestYTDReturn']) else 0.0,
            "worst_ytd_return": float(row['WorstYTDReturn']) if pd.notna(row['WorstYTDReturn']) else 0.0,
            "avg_nav": float(row['AvgNAV']) if pd.notna(row['AvgNAV']) else 0.0,
            "total_positions": int(row['TotalPositions']) if pd.notna(row['TotalPositions']) else 0,
            "funds_with_positions": int(row['FundsWithPositions']) if pd.notna(row['FundsWithPositions']) else 0,
            "total_unrealized_pnl": float(row['TotalUnrealizedPnL']) if pd.notna(row['TotalUnrealizedPnL']) else 0.0,
            "last_updated": date_filter
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary KPIs: {str(e)}")

# ============================================================================
# ANÁLISIS COMPARATIVO ENTRE FONDOS
# ============================================================================

@dashboard_router.get("/compare/performance")
async def compare_fund_performance(
    fund_ids: str = Query(..., description="IDs de fondos separados por coma (ej: 3,5,7)"),
    start_date: Optional[str] = Query("2025-01-01", description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query("2026-03-31", description="Fecha fin (YYYY-MM-DD)")
):
    """
    COMPARATIVO: Performance entre múltiples fondos para análisis competitivo
    """
    try:
        fund_list = [int(x.strip()) for x in fund_ids.split(',')]
        fund_ids_str = ','.join(map(str, fund_list))
        
        engine = get_sql_server_engine()
        
        query = f"""
        SELECT 
            u.PshipID,
            u.Portfolio as FundName,
            u.Fecha,
            u.NAV,
            u.YTDTWR as YTDReturn,
            u.NetEndCap as TotalAssets,
            -- Calcular retorno acumulado desde inicio del período
            u.NAV / FIRST_VALUE(u.NAV) OVER (
                PARTITION BY u.PshipID ORDER BY u.Fecha 
                ROWS UNBOUNDED PRECEDING
            ) - 1 as CumulativeReturn
        FROM [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u
        WHERE u.PshipID IN ({fund_ids_str})
        AND u.Fecha BETWEEN CAST('{start_date}' AS DATE) AND CAST('{end_date}' AS DATE)
        ORDER BY u.PshipID, u.Fecha
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return []
        
        # Formatear para PowerBI
        comparison_data = []
        for _, row in df.iterrows():
            comparison_data.append({
                "fund_id": int(row['PshipID']),
                "fund_name": row['FundName'],
                "date": row['Fecha'].isoformat(),
                "nav": float(row['NAV']) if pd.notna(row['NAV']) else 0.0,
                "ytd_return": float(row['YTDReturn']) if pd.notna(row['YTDReturn']) else 0.0,
                "total_assets": float(row['TotalAssets']) if pd.notna(row['TotalAssets']) else 0.0,
                "cumulative_return": float(row['CumulativeReturn']) if pd.notna(row['CumulativeReturn']) else 0.0
            })
        
        return comparison_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing fund performance: {str(e)}")

# ============================================================================
# EXPORTAR ROUTER
# ============================================================================

# Este router se incluirá en el main.py de la aplicación FastAPI