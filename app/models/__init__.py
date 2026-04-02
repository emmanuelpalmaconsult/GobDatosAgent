"""
Models package for Investment Data Analysis Agent
Contains Pydantic models for API requests and responses.
"""

from .schemas import (
    # Enums
    PortfolioType,
    AssetType,
    TransactionType,
    RiskProfile,
    AnalysisType,
    
    # Base models
    BaseResponse,
    PaginationParams,
    DateRangeFilter,
    
    # Portfolio models
    PortfolioBase,
    PortfolioCreate,
    PortfolioUpdate,
    Portfolio,
    PortfolioSummary,
    
    # Asset models
    AssetBase,
    AssetCreate,
    Asset,
    
    # Transaction models
    TransactionBase,
    TransactionCreate,
    Transaction,
    
    # Cash Flow models
    CashFlowBase,
    CashFlowCreate,
    CashFlow,
    
    # Analysis models
    AnalysisRequest,
    CorrelationAnalysis,
    PerformanceMetrics,
    RiskAnalysis,
    
    # KPI models
    KPIRequest,
    KPIResult,
    PortfolioKPIs,
    KPIDashboard,
    
    # Export models
    ExportRequest,
    ExportResult,
    
    # Table management models
    TableStatus,
    TableConfigUpdate,
    DatabaseStatus,
    
    # Insight models
    InsightRequest,
    Insight,
    InsightResponse
)

__all__ = [
    # Enums
    "PortfolioType",
    "AssetType", 
    "TransactionType",
    "RiskProfile",
    "AnalysisType",
    
    # Base models
    "BaseResponse",
    "PaginationParams",
    "DateRangeFilter",
    
    # Portfolio models
    "PortfolioBase",
    "PortfolioCreate",
    "PortfolioUpdate",
    "Portfolio",
    "PortfolioSummary",
    
    # Asset models
    "AssetBase",
    "AssetCreate",
    "Asset",
    
    # Transaction models
    "TransactionBase",
    "TransactionCreate", 
    "Transaction",
    
    # Cash Flow models
    "CashFlowBase",
    "CashFlowCreate",
    "CashFlow",
    
    # Analysis models
    "AnalysisRequest",
    "CorrelationAnalysis",
    "PerformanceMetrics",
    "RiskAnalysis",
    
    # KPI models
    "KPIRequest",
    "KPIResult",
    "PortfolioKPIs",
    "KPIDashboard",
    
    # Export models  
    "ExportRequest",
    "ExportResult",
    
    # Table management models
    "TableStatus",
    "TableConfigUpdate",
    "DatabaseStatus",
    
    # Insight models
    "InsightRequest",
    "Insight",
    "InsightResponse"
]