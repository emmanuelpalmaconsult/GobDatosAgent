"""
Investment Data Analysis Agent - Main Application
FastAPI backend for intelligent investment data analysis and insights generation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import structlog
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.database.connection import DatabaseManager
from app.api.v1.router import api_router
from app.services.dashboard import dashboard_router  # PowerBI Dashboard


# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Investment Data Analysis Agent")
    
    # Initialize database connection (non-blocking startup)
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        logger.info("✅ Database connection established")
        app.state.db_connected = True
    except Exception as e:
        logger.error("❌ Database connection failed", error=str(e))
        logger.info("⚠️ Starting app without database connection - some endpoints will not work")
        app.state.db_connected = False
        # Don't raise exception to allow app startup
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Investment Data Analysis Agent")
    if hasattr(app.state, 'db_connected') and app.state.db_connected:
        try:
            await db_manager.disconnect()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.warning("⚠️ Error during database cleanup", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="Investment Data Analysis Agent",
    description="""
    🏦 **Business Intelligence Investment Data Analysis Agent**
    
    Aplicación inteligente para análisis de datos de inversión que conecta con SQL Server 
    para extraer insights de portfolios, flujos de caja, transacciones y P&L.
    
    ## 📈 Características Principales
    - **Análisis Inteligente**: Correlaciones automáticas e insights de IA
    - **Gestión Dinámica**: Activar/desactivar tablas dinámicamente  
    - **KPIs en Tiempo Real**: Indicadores financieros calculados automáticamente
    - **Exportación Multi-plataforma**: Power BI, Data Studio, Python Charts
    - **Seguridad Financiera**: Protección de datos y auditoría completa
    
    ## 🔧 Endpoints Disponibles
    - **/portfolios**: Gestión de carteras de inversión
    - **/analysis**: Motor de análisis e insights de IA
    - **/kpis**: Generación de indicadores clave
    - **/exports**: Exportación a herramientas de BI
    - **/health**: Estado del sistema y conexiones
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "portfolios",
            "description": "📊 Gestión y análisis de portfolios de inversión"
        },
        {
            "name": "analysis", 
            "description": "🧠 Motor de análisis inteligente e insights de IA"
        },
        {
            "name": "kpis",
            "description": "📈 Generación de KPIs y métricas financieras"
        },
        {
            "name": "cashflows",
            "description": "💰 Análisis de flujos de caja y liquidez"
        },
        {
            "name": "transactions",
            "description": "🔄 Gestión y análisis detallado de transacciones"
        },
        {
            "name": "exports",
            "description": "📤 Exportación a Power BI, Data Studio y Python"
        },
        {
            "name": "PowerBI Dashboard",
            "description": "📊 Dashboard interactivo con drill-down para PowerBI"
        },
        {
            "name": "health",
            "description": "🏥 Estado del sistema y monitoreo"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router)  # PowerBI Dashboard endpoints

# Static files serving (for exports and charts)
exports_path = Path("exports")
exports_path.mkdir(exist_ok=True)
app.mount("/exports", StaticFiles(directory="exports"), name="exports")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint with system information"""
    return {
        "message": "🏦 Investment Data Analysis Agent",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Portfolio Analysis",
            "AI-Powered Insights", 
            "Dynamic KPI Generation",
            "Multi-Platform Export",
            "Real-time Data Processing"
        ],
        "documentation": "/docs",
        "api_prefix": settings.API_PREFIX
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        db_manager = DatabaseManager()
        db_status = await db_manager.test_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "timestamp": "2026-04-01T12:00:00Z"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
            "timestamp": "2026-04-01T12:00:00Z"
        }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Investment Data Analysis Agent in development mode")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )