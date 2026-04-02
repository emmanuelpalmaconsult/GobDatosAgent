"""
Configuration settings for Investment Data Analysis Agent
Manages environment variables and application settings.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # =============================================================================
    # SOURCE DATABASE CONFIGURATION (Investment Data)
    # =============================================================================
    SOURCE_DB_TYPE: str = Field(default="postgresql")  # postgresql, sqlserver, mysql
    SOURCE_DB_HOST: str = Field(default="localhost")
    SOURCE_DB_PORT: int = Field(default=5432)
    SOURCE_DB_NAME: str = Field(default="InvestmentData")
    SOURCE_DB_USER: str = Field(default="")
    SOURCE_DB_PASSWORD: str = Field(default="")
    
    # =============================================================================
    # ANALYTICS DATABASE CONFIGURATION (PostgreSQL - Analysis Results)
    # =============================================================================
    ANALYTICS_DB_HOST: str = Field(default="localhost")
    ANALYTICS_DB_PORT: int = Field(default=5432)
    ANALYTICS_DB_NAME: str = Field(default="InvestmentAnalytics")
    ANALYTICS_DB_USER: str = Field(default="analytics_user")
    ANALYTICS_DB_PASSWORD: str = Field(default="")
    
    @property
    def source_database_url(self) -> str:
        """Generate source database connection URL"""
        if self.SOURCE_DB_TYPE == "postgresql":
            return (
                f"postgresql+psycopg://{self.SOURCE_DB_USER}:"
                f"{self.SOURCE_DB_PASSWORD}@{self.SOURCE_DB_HOST}:"
                f"{self.SOURCE_DB_PORT}/{self.SOURCE_DB_NAME}"
            )
        elif self.SOURCE_DB_TYPE == "sqlserver":
            # Configuration that works - using Server/Database instead of Data Source/Initial Catalog
            from urllib.parse import quote_plus
            password_encoded = quote_plus(self.SOURCE_DB_PASSWORD)
            username_encoded = quote_plus(self.SOURCE_DB_USER)
            
            return (
                f"mssql+pyodbc://{username_encoded}:"
                f"{password_encoded}@{self.SOURCE_DB_HOST}/{self.SOURCE_DB_NAME}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
                f"&Encrypt=yes&TrustServerCertificate=yes"
                f"&Connection+Timeout=30"
            )
        elif self.SOURCE_DB_TYPE == "mysql":
            return (
                f"mysql+pymysql://{self.SOURCE_DB_USER}:"
                f"{self.SOURCE_DB_PASSWORD}@{self.SOURCE_DB_HOST}:"
                f"{self.SOURCE_DB_PORT}/{self.SOURCE_DB_NAME}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.SOURCE_DB_TYPE}")
    
    @property
    def analytics_database_url(self) -> str:
        """Generate analytics database connection URL (PostgreSQL with psycopg3)"""
        return (
            f"postgresql+psycopg://{self.ANALYTICS_DB_USER}:"
            f"{self.ANALYTICS_DB_PASSWORD}@{self.ANALYTICS_DB_HOST}:"
            f"{self.ANALYTICS_DB_PORT}/{self.ANALYTICS_DB_NAME}"
        )
    
    # =============================================================================
    # APPLICATION SECURITY
    # =============================================================================
    SECRET_KEY: str = Field(default="change-this-super-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    ALGORITHM: str = Field(default="HS256")
    
    # =============================================================================
    # API CONFIGURATION  
    # =============================================================================
    API_PREFIX: str = Field(default="/api/v1")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")
    
    # =============================================================================
    # POWER BI INTEGRATION
    # =============================================================================
    POWERBI_CLIENT_ID: Optional[str] = Field(default=None)
    POWERBI_CLIENT_SECRET: Optional[str] = Field(default=None)
    POWERBI_TENANT_ID: Optional[str] = Field(default=None)
    POWERBI_USERNAME: Optional[str] = Field(default=None)
    POWERBI_PASSWORD: Optional[str] = Field(default=None)
    
    @property
    def powerbi_configured(self) -> bool:
        """Check if Power BI integration is properly configured"""
        return all([
            self.POWERBI_CLIENT_ID,
            self.POWERBI_CLIENT_SECRET,
            self.POWERBI_TENANT_ID
        ])
    
    # =============================================================================
    # GOOGLE DATA STUDIO INTEGRATION
    # =============================================================================
    GOOGLE_SERVICE_ACCOUNT_FILE: Optional[str] = Field(default=None)
    GOOGLE_PROJECT_ID: Optional[str] = Field(default=None)
    
    @property
    def google_configured(self) -> bool:
        """Check if Google Data Studio integration is configured"""
        return all([
            self.GOOGLE_SERVICE_ACCOUNT_FILE,
            self.GOOGLE_PROJECT_ID
        ])
    
    # =============================================================================
    # OPENAI CONFIGURATION
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_MAX_TOKENS: int = Field(default=4000)
    
    @property
    def openai_configured(self) -> bool:
        """Check if OpenAI integration is configured"""
        return self.OPENAI_API_KEY is not None
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="logs/app.log")
    LOG_MAX_SIZE: int = Field(default=10485760)  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5)
    
    # =============================================================================
    # ANALYSIS CONFIGURATION
    # =============================================================================
    MAX_ANALYSIS_RECORDS: int = Field(default=10000)
    CACHE_TTL: int = Field(default=3600)  # 1 hour in seconds
    ANALYSIS_REFRESH_INTERVAL: int = Field(default=15)  # minutes
    ENABLE_AI_ANALYSIS: bool = Field(default=True)
    CACHE_EXPIRY_HOURS: int = Field(default=24)
    MAX_CORRELATION_RECORDS: int = Field(default=10000)
    DEFAULT_ANALYSIS_PERIOD: int = Field(default=30)
    
    # =============================================================================
    # EXPORT CONFIGURATION
    # =============================================================================
    EXPORT_PATH: str = Field(default="exports/")
    REPORT_TEMPLATE_PATH: str = Field(default="templates/")
    CHART_OUTPUT_FORMAT: str = Field(default="png")
    CHART_DPI: int = Field(default=300)
    EXPORT_DIRECTORY: str = Field(default="exports")
    MAX_EXPORT_RECORDS: int = Field(default=50000)
    EXPORT_FORMATS: List[str] = Field(default=["excel", "csv", "json", "powerbi"])
    
    # =============================================================================
    # ADDITIONAL LOGGING CONFIGURATION
    # =============================================================================
    LOG_FORMAT: str = Field(default="detailed")
    LOG_FILE_PATH: str = Field(default="logs/investment_analysis.log")
    
    # =============================================================================
    # DEVELOPMENT/TESTING CONFIGURATION
    # =============================================================================
    DEVELOPMENT_MODE: bool = Field(default=True)
    CREATE_TEST_DATA: bool = Field(default=False)
    ENABLE_DEBUG_ENDPOINTS: bool = Field(default=True)
    
    # =============================================================================
    # PERFORMANCE SETTINGS
    # =============================================================================
    CONNECTION_POOL_SIZE: int = Field(default=20)
    CONNECTION_POOL_OVERFLOW: int = Field(default=10)
    CONNECTION_POOL_TIMEOUT: int = Field(default=30)
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DatabaseSettings(BaseSettings):
    """Database-specific settings and table configurations"""
    
    # =============================================================================
    # INVESTMENT TABLES CONFIGURATION
    # =============================================================================
    
    # Core investment tables
    PORTFOLIOS_TABLE: str = Field(default="Portfolios")
    CASH_FLOWS_TABLE: str = Field(default="CashFlows")
    TRANSACTIONS_TABLE: str = Field(default="Transactions")
    PROFIT_LOSS_TABLE: str = Field(default="ProfitLoss")
    ASSETS_TABLE: str = Field(default="Assets")
    MARKET_DATA_TABLE: str = Field(default="MarketData")
    
    # Additional analysis tables
    PERFORMANCE_TABLE: str = Field(default="Performance")
    RISK_METRICS_TABLE: str = Field(default="RiskMetrics")
    BENCHMARKS_TABLE: str = Field(default="Benchmarks")
    
    # Control tables
    TABLE_CONFIG_TABLE: str = Field(default="TableConfiguration")
    ANALYSIS_JOBS_TABLE: str = Field(default="AnalysisJobs")
    
    @property
    def core_tables(self) -> List[str]:
        """List of core investment tables"""
        return [
            self.PORTFOLIOS_TABLE,
            self.CASH_FLOWS_TABLE,
            self.TRANSACTIONS_TABLE,
            self.PROFIT_LOSS_TABLE,
            self.ASSETS_TABLE,
            self.MARKET_DATA_TABLE
        ]
    
    @property
    def analysis_tables(self) -> List[str]:
        """List of analysis and metrics tables"""
        return [
            self.PERFORMANCE_TABLE,
            self.RISK_METRICS_TABLE,
            self.BENCHMARKS_TABLE
        ]
    
    @property
    def control_tables(self) -> List[str]:
        """List of control and configuration tables"""
        return [
            self.TABLE_CONFIG_TABLE,
            self.ANALYSIS_JOBS_TABLE
        ]
    
    @property
    def all_tables(self) -> List[str]:
        """All available tables"""
        return self.core_tables + self.analysis_tables + self.control_tables


class KPISettings(BaseSettings):
    """KPI calculation and monitoring settings"""
    
    # =============================================================================
    # KPI CALCULATION SETTINGS
    # =============================================================================
    
    # Risk-free rate for Sharpe ratio calculation (annual %)
    RISK_FREE_RATE: float = Field(default=0.02)  # 2%
    
    # Default analysis periods (in days)
    SHORT_TERM_PERIOD: int = Field(default=30)    # 1 month
    MEDIUM_TERM_PERIOD: int = Field(default=90)   # 3 months
    LONG_TERM_PERIOD: int = Field(default=365)    # 1 year
    
    # Performance thresholds
    VOLATILITY_THRESHOLD: float = Field(default=0.15)  # 15%
    DRAWDOWN_THRESHOLD: float = Field(default=0.10)    # 10%
    
    # Update frequencies (in minutes)
    REALTIME_KPI_REFRESH: int = Field(default=5)      # 5 minutes
    DAILY_KPI_REFRESH: int = Field(default=1440)      # 24 hours
    MONTHLY_KPI_REFRESH: int = Field(default=43200)   # 30 days


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings"""
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings"""
    return DatabaseSettings()


@lru_cache()
def get_kpi_settings() -> KPISettings:
    """Get cached KPI settings"""
    return KPISettings()


# Global settings instances
settings = get_settings()
db_settings = get_database_settings()
kpi_settings = get_kpi_settings()