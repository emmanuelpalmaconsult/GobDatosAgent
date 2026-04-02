"""
Investment Data Models - Core financial data structures
SQLAlchemy models for investment tables: portfolios, transactions, cash flows, P&L
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class Portfolio(Base):
    """Portfolio model - represents investment portfolios"""
    __tablename__ = "Portfolios"
    
    portfolio_id = Column(Integer, primary_key=True, index=True)
    portfolio_code = Column(String(50), unique=True, nullable=False, index=True)
    portfolio_name = Column(String(200), nullable=False)
    portfolio_type = Column(String(50), nullable=False)  # equity, fixed_income, mixed, alternative
    currency = Column(String(3), nullable=False, default="USD")
    inception_date = Column(Date, nullable=False)
    manager_name = Column(String(100))
    benchmark = Column(String(100))
    risk_profile = Column(String(20))  # conservative, moderate, aggressive
    status = Column(String(20), nullable=False, default="active")  # active, inactive, closed
    
    # Investment limits and constraints
    max_investment = Column(Numeric(18, 2))
    min_investment = Column(Numeric(18, 2))
    management_fee = Column(Numeric(5, 4))  # As decimal (0.0150 = 1.5%)
    performance_fee = Column(Numeric(5, 4))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="portfolio")
    cash_flows = relationship("CashFlow", back_populates="portfolio")
    performance_records = relationship("Performance", back_populates="portfolio")


class Asset(Base):
    """Asset model - represents financial instruments"""
    __tablename__ = "Assets"
    
    asset_id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False, index=True)  # ISIN, TICKER, etc.
    asset_name = Column(String(200), nullable=False)
    asset_type = Column(String(50), nullable=False)  # stock, bond, etf, mutual_fund, derivative, commodity
    asset_class = Column(String(50))  # equity, fixed_income, alternative, cash
    sector = Column(String(100))
    country = Column(String(50))
    currency = Column(String(3), nullable=False)
    
    # Market data
    exchange = Column(String(50))
    listing_date = Column(Date)
    market_cap = Column(Numeric(18, 2))
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="asset")
    market_data = relationship("MarketData", back_populates="asset")


class Transaction(Base):
    """Transaction model - records all portfolio transactions"""
    __tablename__ = "Transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    transaction_code = Column(String(50), unique=True, nullable=False)
    
    # Foreign keys
    portfolio_id = Column(Integer, ForeignKey("Portfolios.portfolio_id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("Assets.asset_id"), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(String(20), nullable=False)  # buy, sell, dividend, interest, fee
    transaction_date = Column(Date, nullable=False, index=True)
    settlement_date = Column(Date)
    
    # Quantities and prices
    quantity = Column(Numeric(18, 6), nullable=False)
    price = Column(Numeric(18, 6), nullable=False)
    gross_amount = Column(Numeric(18, 2), nullable=False)  # quantity * price
    fees = Column(Numeric(18, 2), default=0)
    taxes = Column(Numeric(18, 2), default=0)
    net_amount = Column(Numeric(18, 2), nullable=False)  # gross_amount - fees - taxes
    
    # Currency and exchange
    transaction_currency = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(10, 6), default=1.0)
    base_currency_amount = Column(Numeric(18, 2))  # net_amount * exchange_rate
    
    # Additional information
    broker = Column(String(100))
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")


class CashFlow(Base):
    """Cash flow model - tracks portfolio cash movements"""
    __tablename__ = "CashFlows"
    
    cashflow_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    portfolio_id = Column(Integer, ForeignKey("Portfolios.portfolio_id"), nullable=False, index=True)
    
    # Cash flow details
    flow_date = Column(Date, nullable=False, index=True)
    flow_type = Column(String(20), nullable=False)  # inflow, outflow, dividend, distribution
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Classification
    flow_category = Column(String(50))  # subscription, redemption, dividend, interest, fee
    counterparty = Column(String(100))
    
    # Additional information
    description = Column(Text)
    reference_id = Column(String(50))  # External reference
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="cash_flows")


class ProfitLoss(Base):
    """P&L model - profit and loss records"""
    __tablename__ = "ProfitLoss"
    
    pl_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    portfolio_id = Column(Integer, ForeignKey("Portfolios.portfolio_id"), nullable=False, index=True)
    
    # Period information
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, monthly, quarterly, annual
    
    # P&L components
    realized_pnl = Column(Numeric(18, 2), default=0)  # From closed positions
    unrealized_pnl = Column(Numeric(18, 2), default=0)  # From open positions
    total_pnl = Column(Numeric(18, 2), nullable=False)  # realized + unrealized
    
    # Revenue components
    dividend_income = Column(Numeric(18, 2), default=0)
    interest_income = Column(Numeric(18, 2), default=0)
    capital_gains = Column(Numeric(18, 2), default=0)
    capital_losses = Column(Numeric(18, 2), default=0)
    
    # Cost components
    management_fees = Column(Numeric(18, 2), default=0)
    transaction_costs = Column(Numeric(18, 2), default=0)
    other_expenses = Column(Numeric(18, 2), default=0)
    
    # Portfolio values
    beginning_value = Column(Numeric(18, 2), nullable=False)
    ending_value = Column(Numeric(18, 2), nullable=False)
    average_value = Column(Numeric(18, 2))
    
    # Performance metrics
    return_percentage = Column(Numeric(8, 4))  # Total return as percentage
    
    # Currency
    currency = Column(String(3), nullable=False, default="USD")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MarketData(Base):
    """Market data model - historical and current market prices"""
    __tablename__ = "MarketData"
    
    market_data_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    asset_id = Column(Integer, ForeignKey("Assets.asset_id"), nullable=False, index=True)
    
    # Date and pricing
    price_date = Column(Date, nullable=False, index=True)
    open_price = Column(Numeric(18, 6))
    high_price = Column(Numeric(18, 6))
    low_price = Column(Numeric(18, 6))
    close_price = Column(Numeric(18, 6), nullable=False)
    adjusted_close = Column(Numeric(18, 6))
    volume = Column(Numeric(18, 0))
    
    # Additional market metrics
    market_cap = Column(Numeric(18, 2))
    pe_ratio = Column(Numeric(8, 2))
    dividend_yield = Column(Numeric(6, 4))
    
    # Data source
    data_source = Column(String(50))  # bloomberg, yahoo, manual, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="market_data")


class Performance(Base):
    """Performance model - calculated performance metrics"""
    __tablename__ = "Performance"
    
    performance_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    portfolio_id = Column(Integer, ForeignKey("Portfolios.portfolio_id"), nullable=False, index=True)
    
    # Period information
    calculation_date = Column(Date, nullable=False, index=True)
    period_days = Column(Integer, nullable=False)  # 1, 30, 90, 365, etc.
    
    # Return metrics
    total_return = Column(Numeric(8, 4))  # Total return percentage
    annualized_return = Column(Numeric(8, 4))  # Annualized return percentage
    
    # Risk metrics
    volatility = Column(Numeric(8, 4))  # Standard deviation of returns
    sharpe_ratio = Column(Numeric(8, 4))  # Risk-adjusted return
    max_drawdown = Column(Numeric(8, 4))  # Maximum peak-to-trough decline
    
    # Additional metrics
    alpha = Column(Numeric(8, 4))  # Excess return vs benchmark
    beta = Column(Numeric(8, 4))  # Market sensitivity
    information_ratio = Column(Numeric(8, 4))
    tracking_error = Column(Numeric(8, 4))
    
    # Benchmark comparison
    benchmark_return = Column(Numeric(8, 4))
    excess_return = Column(Numeric(8, 4))  # Portfolio return - benchmark return
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="performance_records")


class RiskMetrics(Base):
    """Risk metrics model - detailed risk analysis"""
    __tablename__ = "RiskMetrics"
    
    risk_id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    portfolio_id = Column(Integer, ForeignKey("Portfolios.portfolio_id"), nullable=False, index=True)
    
    # Date and period
    calculation_date = Column(Date, nullable=False, index=True)
    period_days = Column(Integer, nullable=False)
    
    # Value at Risk metrics
    var_95 = Column(Numeric(18, 2))  # 95% Value at Risk
    var_99 = Column(Numeric(18, 2))  # 99% Value at Risk
    expected_shortfall = Column(Numeric(18, 2))  # Conditional VaR
    
    # Risk decomposition
    systematic_risk = Column(Numeric(8, 4))
    specific_risk = Column(Numeric(8, 4))
    
    # Concentration risk
    top_10_concentration = Column(Numeric(6, 4))  # % in top 10 holdings
    sector_concentration = Column(Numeric(6, 4))  # Max sector weight
    
    # Liquidity risk
    liquidity_score = Column(Numeric(6, 2))
    
    # Currency risk
    currency_exposure = Column(Numeric(6, 4))  # Non-base currency %
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class TableConfiguration(Base):
    """Table configuration model - manages active/inactive tables"""
    __tablename__ = "TableConfiguration"
    
    config_id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)
    
    # Analysis settings
    analysis_priority = Column(Integer, default=1)  # 1=high, 5=low
    refresh_frequency = Column(String(20), default="daily")  # realtime, hourly, daily, weekly
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisJob(Base):
    """Analysis job model - tracks analysis executions"""
    __tablename__ = "AnalysisJobs"
    
    job_id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(100), nullable=False)
    job_type = Column(String(50), nullable=False)  # correlation, kpi, export, insight
    
    # Execution details
    status = Column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Configuration
    parameters = Column(Text)  # JSON string with job parameters
    tables_analyzed = Column(Text)  # Comma-separated list of tables
    
    # Results
    records_processed = Column(Integer)
    output_path = Column(String(500))
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)