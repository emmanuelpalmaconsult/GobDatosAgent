"""
Investment Data Analysis Agent - Demo Server
Servidor demo para desarrollo del dashboard PowerBI sin dependencias de SQL Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from datetime import datetime

from app.api.v1.endpoints.powerbi_demo import router as demo_router

# Configuración de la aplicación
app = FastAPI(
    title="Investment Data Analysis Agent - Demo",
    description="Demo server para desarrollo del dashboard PowerBI",
    version="1.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS para PowerBI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas demo
app.include_router(
    demo_router, 
    prefix="/api/v1/powerbi-demo", 
    tags=["PowerBI Demo Dashboard"]
)

@app.get("/")
async def root():
    """Redirect a la documentación"""
    return RedirectResponse(url="/docs")

@app.get("/api/v1/health")
async def health_check():
    """Health check general del sistema demo"""
    return {
        "status": "healthy",
        "service": "Investment Data Analysis Agent",
        "mode": "demo",
        "version": "1.0.0-demo",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "powerbi_demo": "✅ Available",
            "sql_server": "❌ Unavailable (demo mode)",
            "postgresql": "✅ Available"
        }
    }

@app.get("/api/v1/info")
async def system_info():
    """Información del sistema demo"""
    return {
        "system": "Investment Data Analysis Agent",
        "mode": "demo",
        "description": "Demo server for PowerBI dashboard development",
        "features": [
            "52 synthetic investment funds",
            "Realistic market data simulation",
            "PowerBI-optimized endpoints",
            "Real-time performance metrics",
            "Portfolio analytics and KPIs"
        ],
        "demo_endpoints": [
            "/api/v1/powerbi-demo/funds-overview",
            "/api/v1/powerbi-demo/fund-positions/{fund_id}",
            "/api/v1/powerbi-demo/fund-performance/{fund_id}",
            "/api/v1/powerbi-demo/portfolio-analytics",
            "/api/v1/powerbi-demo/kpis-dashboard"
        ],
        "documentation": "/docs",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Investment Data Analysis Agent - Demo Mode")
    print("📊 PowerBI Dashboard development ready")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 Documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main_demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )