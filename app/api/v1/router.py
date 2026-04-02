"""
Main API Router for Investment Data Analysis Agent v1
Aggregates all endpoint routers for the API.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import portfolios, analysis, kpis, exports, health, cashflows, transactions, sql_server_direct, powerbi_dashboard, sql_server_discovery, powerbi_real_data, powerbi_quick_real

api_router = APIRouter()

# Include PowerBI Quick Real endpoints (WORKING VERSION)
api_router.include_router(
    powerbi_quick_real.router,
    tags=["PowerBI Quick Real"]
)

# Include PowerBI REAL Data endpoints (100% REAL SQL SERVER DATA)
api_router.include_router(
    powerbi_real_data.router,
    tags=["PowerBI Real Data"]
)

# Include SQL Server Discovery endpoints (FIND REAL TABLES)
api_router.include_router(
    sql_server_discovery.router,
    tags=["SQL Server Discovery"]
)

# Include PowerBI Dashboard endpoints (OPTIMIZED FOR POWERBI)
api_router.include_router(
    powerbi_dashboard.router,
    tags=["PowerBI Dashboard"]
)

# Include SQL Server Direct endpoints (REAL DATA)
api_router.include_router(
    sql_server_direct.router,
    tags=["SQL Server Direct"]
)

# Include all endpoint routers
api_router.include_router(
    health.router, 
    prefix="/health", 
    tags=["health"]
)

api_router.include_router(
    portfolios.router, 
    prefix="/portfolios", 
    tags=["portfolios"]
)

api_router.include_router(
    analysis.router, 
    prefix="/analysis", 
    tags=["analysis"]
)

api_router.include_router(
    kpis.router, 
    prefix="/kpis", 
    tags=["kpis"]
)

api_router.include_router(
    cashflows.router, 
    prefix="/cashflows", 
    tags=["cashflows"]
)

api_router.include_router(
    transactions.router, 
    prefix="/transactions", 
    tags=["transactions"]
)

api_router.include_router(
    exports.router, 
    prefix="/exports", 
    tags=["exports"]
)