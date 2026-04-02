"""
PowerBI Demo Dashboard Endpoints
Endpoints diseñados para funcionar sin conectividad a SQL Server
Datos simulados pero realistas para desarrollo del dashboard
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from decimal import Decimal

router = APIRouter()

# Datos demo para 52 fondos de inversión
DEMO_FUNDS = [
    {"PshipID": i, "FundName": f"Fondo {['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'][i % 8]} {i:02d}", 
     "FundType": random.choice(["Equity", "Fixed Income", "Mixed", "Real Estate", "Commodity"]),
     "TotalAssets": round(random.uniform(500_000_000, 15_000_000_000), 2),
     "YTDReturn": round(random.uniform(-15.5, 25.8), 2),
     "Benchmark": f"Benchmark {i % 5}",
     "RiskLevel": random.choice([1, 2, 3, 4, 5]),
     "Currency": random.choice(["CLP", "USD", "EUR"]),
     "InceptionDate": "2020-01-15",
     "Status": "Active"} for i in range(1, 53)
]

@router.get("/funds-overview")
async def get_funds_overview():
    """Endpoint principal para overview de fondos en PowerBI"""
    try:
        return {
            "success": True,
            "data": DEMO_FUNDS,
            "summary": {
                "total_funds": len(DEMO_FUNDS),
                "total_aum": sum(f["TotalAssets"] for f in DEMO_FUNDS),
                "avg_ytd_return": sum(f["YTDReturn"] for f in DEMO_FUNDS) / len(DEMO_FUNDS),
                "active_funds": len([f for f in DEMO_FUNDS if f["Status"] == "Active"])
            },
            "timestamp": datetime.now().isoformat(),
            "mode": "demo"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo funds error: {str(e)}")

@router.get("/fund-positions/{fund_id}")
async def get_fund_positions(fund_id: int):
    """Posiciones detalladas por fondo"""
    if fund_id < 1 or fund_id > 52:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    # Generar posiciones simuladas para el fondo específico
    positions = []
    for i in range(random.randint(15, 35)):
        position = {
            "PshipID": fund_id,
            "SecurityID": f"SEC{fund_id:02d}{i:03d}",
            "SecurityName": f"Security {random.choice(['Tech Corp', 'Bank SA', 'Mining Ltd', 'Energy Inc', 'Retail Co'])} {i}",
            "AssetClass": random.choice(["Equity", "Fixed Income", "Cash", "Alternative"]),
            "Sector": random.choice(["Technology", "Financial", "Mining", "Energy", "Consumer"]),
            "MarketValue": round(random.uniform(10_000_000, 500_000_000), 2),
            "Weight": round(random.uniform(0.5, 8.5), 2),
            "Shares": random.randint(10000, 500000),
            "Price": round(random.uniform(50, 2500), 2),
            "Currency": random.choice(["CLP", "USD", "EUR"]),
            "LastUpdate": datetime.now().isoformat()
        }
        positions.append(position)
    
    return {
        "success": True,
        "fund_id": fund_id,
        "positions": positions,
        "total_positions": len(positions),
        "total_market_value": sum(p["MarketValue"] for p in positions),
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    }

@router.get("/fund-performance/{fund_id}")
async def get_fund_performance(fund_id: int, months: int = 12):
    """Performance mensual de un fondo específico"""
    if fund_id < 1 or fund_id > 52:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    # Generar datos de performance histórica
    performance_data = []
    base_date = datetime.now() - timedelta(days=30 * months)
    current_value = 100.0  # Valor base índice
    
    for i in range(months + 1):
        month_date = base_date + timedelta(days=30 * i)
        # Simulación realista de variación mensual
        monthly_return = random.uniform(-8.5, 12.3)
        current_value *= (1 + monthly_return / 100)
        
        performance_data.append({
            "Date": month_date.strftime("%Y-%m-%d"),
            "NAV": round(current_value, 4),
            "MonthlyReturn": round(monthly_return, 2),
            "AccumulatedReturn": round(((current_value - 100) / 100) * 100, 2),
            "Benchmark": round(current_value * random.uniform(0.92, 1.08), 4),
            "Assets": round(DEMO_FUNDS[fund_id-1]["TotalAssets"] * random.uniform(0.95, 1.05), 2)
        })
    
    return {
        "success": True,
        "fund_id": fund_id,
        "performance": performance_data,
        "summary": {
            "total_return": round(((current_value - 100) / 100) * 100, 2),
            "volatility": round(random.uniform(8.5, 25.2), 2),
            "sharpe_ratio": round(random.uniform(0.45, 2.15), 2),
            "max_drawdown": round(random.uniform(-15.5, -2.1), 2)
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    }

@router.get("/portfolio-analytics")
async def get_portfolio_analytics():
    """Analytics agregados de todo el portafolio"""
    
    # Cálculos agregados
    total_aum = sum(f["TotalAssets"] for f in DEMO_FUNDS)
    avg_return = sum(f["YTDReturn"] for f in DEMO_FUNDS) / len(DEMO_FUNDS)
    
    # Distribución por tipo de activo
    asset_allocation = {
        "Equity": round(total_aum * 0.65, 2),
        "Fixed Income": round(total_aum * 0.25, 2),
        "Mixed": round(total_aum * 0.08, 2),
        "Real Estate": round(total_aum * 0.015, 2),
        "Commodity": round(total_aum * 0.005, 2)
    }
    
    # Top performers
    top_performers = sorted(DEMO_FUNDS, key=lambda x: x["YTDReturn"], reverse=True)[:5]
    bottom_performers = sorted(DEMO_FUNDS, key=lambda x: x["YTDReturn"])[:3]
    
    # Risk metrics
    risk_distribution = {
        "Low Risk (1-2)": len([f for f in DEMO_FUNDS if f["RiskLevel"] <= 2]),
        "Medium Risk (3)": len([f for f in DEMO_FUNDS if f["RiskLevel"] == 3]),
        "High Risk (4-5)": len([f for f in DEMO_FUNDS if f["RiskLevel"] >= 4])
    }
    
    return {
        "success": True,
        "summary": {
            "total_funds": len(DEMO_FUNDS),
            "total_aum": total_aum,
            "average_return": avg_return,
            "active_funds": len([f for f in DEMO_FUNDS if f["Status"] == "Active"])
        },
        "asset_allocation": asset_allocation,
        "performance": {
            "top_performers": top_performers,
            "bottom_performers": bottom_performers
        },
        "risk_analysis": risk_distribution,
        "currency_breakdown": {
            "CLP": round(total_aum * 0.70, 2),
            "USD": round(total_aum * 0.25, 2),
            "EUR": round(total_aum * 0.05, 2)
        },
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    }

@router.get("/kpis-dashboard")
async def get_kpis_dashboard():
    """KPIs principales para el dashboard ejecutivo"""
    
    total_aum = sum(f["TotalAssets"] for f in DEMO_FUNDS)
    
    kpis = {
        "aum_total": {
            "value": total_aum,
            "currency": "CLP",
            "change_pct": round(random.uniform(-5.2, 8.7), 2),
            "trend": "up" if random.random() > 0.3 else "down"
        },
        "average_return": {
            "value": round(sum(f["YTDReturn"] for f in DEMO_FUNDS) / len(DEMO_FUNDS), 2),
            "benchmark": 6.5,
            "outperformance": True
        },
        "active_funds": {
            "value": len([f for f in DEMO_FUNDS if f["Status"] == "Active"]),
            "total": len(DEMO_FUNDS),
            "percentage": round((len([f for f in DEMO_FUNDS if f["Status"] == "Active"]) / len(DEMO_FUNDS)) * 100, 1)
        },
        "risk_score": {
            "portfolio_risk": round(random.uniform(2.5, 4.2), 1),
            "max_risk": 5.0,
            "risk_level": "Medium"
        },
        "top_fund": {
            "name": max(DEMO_FUNDS, key=lambda x: x["YTDReturn"])["FundName"],
            "return": max(f["YTDReturn"] for f in DEMO_FUNDS),
            "aum": max(DEMO_FUNDS, key=lambda x: x["YTDReturn"])["TotalAssets"]
        }
    }
    
    return {
        "success": True,
        "kpis": kpis,
        "alerts": [
            {"type": "info", "message": f"Portfolio performance above benchmark by {round(random.uniform(0.5, 3.2), 1)}%"},
            {"type": "warning", "message": "2 funds require risk assessment review"},
            {"type": "success", "message": f"AUM growth of {round(random.uniform(2.1, 7.3), 1)}% this quarter"}
        ],
        "timestamp": datetime.now().isoformat(),
        "mode": "demo"
    }

@router.get("/health")
async def health_check():
    """Health check para verificar disponibilidad del servicio demo"""
    return {
        "status": "healthy",
        "service": "PowerBI Demo Dashboard",
        "mode": "demo",
        "endpoints": 6,
        "synthetic_funds": len(DEMO_FUNDS),
        "timestamp": datetime.now().isoformat()
    }