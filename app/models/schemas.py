"""
Pydantic Models for Investment Data Analysis Agent
Request and response models for FastAPI endpoints.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class PortfolioType(str, Enum):
    """Portfolio type enumeration"""
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    MIXED = "mixed"
    ALTERNATIVE = "alternative"
    CASH = "cash"


class AssetType(str, Enum):
    """Asset type enumeration"""
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    DERIVATIVE = "derivative"
    COMMODITY = "commodity"
    CASH = "cash"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    FEE = "fee"
    SPLIT = "split"
    MERGER = "merger"


class RiskProfile(str, Enum):
    """Risk profile enumeration"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class AnalysisType(str, Enum):
    """Analysis type enumeration"""
    CORRELATION = "correlation"
    PERFORMANCE = "performance"
    RISK = "risk"
    ALLOCATION = "allocation"
    CASH_FLOW = "cash_flow"
    BENCHMARK = "benchmark"


# =============================================================================
# BASE MODELS
# =============================================================================

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=50, ge=1, le=1000)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class DateRangeFilter(BaseModel):
    """Date range filter"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


# =============================================================================
# PORTFOLIO MODELS
# =============================================================================

class PortfolioBase(BaseModel):
    """Portfolio base model"""
    portfolio_code: str = Field(..., min_length=1, max_length=50)
    portfolio_name: str = Field(..., min_length=1, max_length=200)
    portfolio_type: PortfolioType
    currency: str = Field(..., min_length=3, max_length=3)
    inception_date: date
    manager_name: Optional[str] = Field(None, max_length=100)
    benchmark: Optional[str] = Field(None, max_length=100)
    risk_profile: Optional[RiskProfile] = None
    max_investment: Optional[Decimal] = None
    min_investment: Optional[Decimal] = None
    management_fee: Optional[Decimal] = Field(None, ge=0, le=1)
    performance_fee: Optional[Decimal] = Field(None, ge=0, le=1)


class PortfolioCreate(PortfolioBase):
    """Portfolio creation model"""
    pass


class PortfolioUpdate(BaseModel):
    """Portfolio update model"""
    portfolio_name: Optional[str] = Field(None, min_length=1, max_length=200)
    manager_name: Optional[str] = Field(None, max_length=100)
    benchmark: Optional[str] = Field(None, max_length=100)
    risk_profile: Optional[RiskProfile] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|closed)$")


class Portfolio(PortfolioBase):
    """Portfolio response model"""
    portfolio_id: int
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Portfolio summary with key metrics"""
    portfolio_id: int
    portfolio_code: str
    portfolio_name: str
    portfolio_type: PortfolioType
    current_value: Decimal
    total_return: Optional[Decimal] = None
    return_percentage: Optional[Decimal] = None
    volatility: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    last_updated: datetime


# =============================================================================
# ASSET MODELS
# =============================================================================

class AssetBase(BaseModel):
    """Asset base model"""
    asset_code: str = Field(..., min_length=1, max_length=50)
    asset_name: str = Field(..., min_length=1, max_length=200)
    asset_type: AssetType
    asset_class: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    currency: str = Field(..., min_length=3, max_length=3)
    exchange: Optional[str] = Field(None, max_length=50)


class AssetCreate(AssetBase):
    """Asset creation model"""
    pass


class Asset(AssetBase):
    """Asset response model"""
    asset_id: int
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# TRANSACTION MODELS
# =============================================================================

class TransactionBase(BaseModel):
    """Transaction base model"""
    portfolio_id: int
    asset_id: int
    transaction_type: TransactionType
    transaction_date: date
    settlement_date: Optional[date] = None
    quantity: Decimal
    price: Decimal
    fees: Decimal = Field(default=Decimal('0'), ge=0)
    taxes: Decimal = Field(default=Decimal('0'), ge=0)
    transaction_currency: str = Field(..., min_length=3, max_length=3)
    exchange_rate: Decimal = Field(default=Decimal('1.0'), gt=0)
    broker: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Transaction creation model"""
    pass


class Transaction(TransactionBase):
    """Transaction response model"""
    transaction_id: int
    transaction_code: str
    gross_amount: Decimal
    net_amount: Decimal
    base_currency_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# CASH FLOW MODELS
# =============================================================================

class CashFlowBase(BaseModel):
    """Cash flow base model"""
    portfolio_id: int
    flow_date: date
    flow_type: str = Field(..., pattern="^(inflow|outflow|dividend|distribution)$")
    amount: Decimal
    currency: str = Field(..., min_length=3, max_length=3)
    flow_category: Optional[str] = Field(None, max_length=50)
    counterparty: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    reference_id: Optional[str] = Field(None, max_length=50)


class CashFlowCreate(CashFlowBase):
    """Cash flow creation model"""
    pass


class CashFlow(CashFlowBase):
    """Cash flow response model"""
    cashflow_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# ANALYSIS MODELS
# =============================================================================

class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analysis_type: AnalysisType
    portfolio_ids: List[int] = Field(..., min_items=1)
    date_range: Optional[DateRangeFilter] = None
    parameters: Optional[Dict[str, Any]] = None
    include_benchmark: bool = True


class CorrelationAnalysis(BaseModel):
    """Correlation analysis result"""
    portfolio_id: int
    correlations: Dict[str, float]
    correlation_matrix: List[List[float]]
    asset_labels: List[str]
    analysis_date: date
    period_days: int


class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    portfolio_id: int
    calculation_date: date
    period_days: int
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    benchmark_return: Optional[float] = None


class RiskAnalysis(BaseModel):
    """Risk analysis model"""
    portfolio_id: int
    calculation_date: date
    var_95: Optional[float] = None
    var_99: Optional[float] = None
    expected_shortfall: Optional[float] = None
    systematic_risk: Optional[float] = None
    specific_risk: Optional[float] = None
    concentration_risk: Optional[float] = None
    liquidity_score: Optional[float] = None


# =============================================================================
# KPI MODELS
# =============================================================================

class KPIRequest(BaseModel):
    """KPI calculation request"""
    portfolio_ids: List[int] = Field(..., min_items=1)
    kpi_types: List[str] = Field(..., min_items=1)
    calculation_date: Optional[date] = None
    benchmark_code: Optional[str] = None


class KPIResult(BaseModel):
    """Individual KPI result"""
    kpi_name: str
    kpi_value: Union[float, str, int]
    kpi_unit: Optional[str] = None
    benchmark_value: Optional[float] = None
    status: str = Field(default="normal")  # normal, warning, critical
    calculation_date: date


class PortfolioKPIs(BaseModel):
    """Portfolio KPIs collection"""
    portfolio_id: int
    portfolio_code: str
    calculation_date: date
    kpis: List[KPIResult]
    summary_score: Optional[float] = None  # Overall portfolio health score


class KPIDashboard(BaseResponse):
    """KPI Dashboard response"""
    portfolios: List[PortfolioKPIs]
    market_overview: Optional[Dict[str, Any]] = None
    alerts: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# EXPORT MODELS
# =============================================================================

class ExportRequest(BaseModel):
    """Export request model"""
    export_type: str = Field(..., pattern="^(powerbi|datastudio|excel|python_chart)$")
    portfolio_ids: List[int] = Field(..., min_items=1)
    data_types: List[str] = Field(..., min_items=1)  # portfolios, transactions, kpis, etc.
    date_range: Optional[DateRangeFilter] = None
    export_format: str = Field(default="auto")
    include_charts: bool = True
    destination_path: Optional[str] = None


class ExportResult(BaseResponse):
    """Export result model"""
    export_id: str
    export_type: str
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    record_count: int
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None


# =============================================================================
# TABLE MANAGEMENT MODELS
# =============================================================================

class TableStatus(BaseModel):
    """Table status model"""
    table_name: str
    is_active: bool
    record_count: int
    last_updated: Optional[datetime] = None
    analysis_priority: int = 1
    refresh_frequency: str = "daily"


class TableConfigUpdate(BaseModel):
    """Table configuration update"""
    is_active: Optional[bool] = None
    analysis_priority: Optional[int] = Field(None, ge=1, le=5)
    refresh_frequency: Optional[str] = Field(None, pattern="^(realtime|hourly|daily|weekly)$")


class DatabaseStatus(BaseResponse):
    """Database status response"""
    connection_status: str
    total_tables: int
    active_tables: int
    table_details: List[TableStatus]
    last_analysis: Optional[datetime] = None


# =============================================================================
# INSIGHT MODELS
# =============================================================================

class InsightRequest(BaseModel):
    """AI insight generation request"""
    portfolio_ids: List[int] = Field(..., min_items=1)
    insight_types: List[str] = Field(default=["performance", "risk", "allocation"])
    time_horizon: str = Field(default="month", pattern="^(week|month|quarter|year)$")
    include_recommendations: bool = True


class Insight(BaseModel):
    """Individual insight"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    importance: str = Field(pattern="^(low|medium|high|critical)$")
    confidence: float = Field(ge=0, le=1)
    recommendation: Optional[str] = None
    supporting_data: Optional[Dict[str, Any]] = None
    generated_at: datetime


class InsightResponse(BaseResponse):
    """Insight generation response"""
    portfolio_id: int
    insights: List[Insight]
    summary: str
    next_review_date: Optional[date] = None