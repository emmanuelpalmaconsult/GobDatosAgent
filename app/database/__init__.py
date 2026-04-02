"""
Database package for Investment Data Analysis Agent
Contains SQLAlchemy models, connection management, and database utilities.
"""

from .connection import DatabaseManager
from .models import (
    Base,
    Portfolio,
    Asset,
    Transaction,
    CashFlow,
    ProfitLoss,
    MarketData,
    Performance,
    RiskMetrics,
    TableConfiguration,
    AnalysisJob
)

__all__ = [
    "DatabaseManager",
    "Base",
    "Portfolio",
    "Asset", 
    "Transaction",
    "CashFlow",
    "ProfitLoss",
    "MarketData",
    "Performance",
    "RiskMetrics",
    "TableConfiguration",
    "AnalysisJob"
]