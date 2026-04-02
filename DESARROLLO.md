# Investment Data Analysis Agent - Guía de Desarrollo

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
app/
├── core/                   # Configuración y utilidades centrales
│   ├── config.py          # Configuración de la aplicación
│   └── logging_config.py  # Configuración de logging
├── database/              # Capa de datos
│   ├── connection.py      # Gestor de conexiones BD
│   └── models.py          # Modelos SQLAlchemy
├── models/                # Modelos Pydantic para API
│   └── schemas.py         # Esquemas de request/response
├── services/              # Lógica de negocio
│   └── investment_service.py  # Servicio principal
├── analysis/              # Motor de análisis IA
│   └── ai_service.py      # Servicio de análisis inteligente
├── kpis/                  # Generador de KPIs
│   └── calculator.py      # Calculadora de métricas
├── exports/               # Exportación BI
│   └── bi_service.py      # Servicio de exportación
└── api/                   # Endpoints FastAPI
    └── v1/
        ├── router.py      # Router principal
        └── endpoints/     # Endpoints individuales
```

### Flujo de Datos

1. **Ingesta**: Datos de inversión desde SQL Server
2. **Procesamiento**: Análisis IA + KPIs calculados
3. **Insights**: Generación de insights automáticos
4. **Exportación**: Power BI, Data Studio, Excel, Python

## 🔧 Configuración del Entorno

### Prerrequisitos

- Python 3.9+
- SQL Server (con datos de inversión)
- Credenciales de acceso a BD

### Variables de Entorno (.env)

```bash
# Base de Datos
SQL_SERVER_HOST=tu-servidor
SQL_SERVER_DATABASE=InvestmentDB
SQL_SERVER_USERNAME=usuario
SQL_SERVER_PASSWORD=password

# Seguridad
SECRET_KEY=tu-clave-secreta

# Integraciones BI
POWERBI_CLIENT_ID=cliente-powerbi
POWERBI_CLIENT_SECRET=secreto-powerbi
OPENAI_API_KEY=clave-openai
```

### Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 4. Ejecutar aplicación
python -m uvicorn app.main:app --reload
```

## 📊 Estructura de Base de Datos

### Tablas Principales

#### Portfolios
- `portfolio_id` (PK)
- `portfolio_code` (Unique)
- `portfolio_name`
- `portfolio_type` (equity, fixed_income, mixed, alternative)
- `currency`
- `inception_date`
- `manager_name`
- `risk_profile` (conservative, moderate, aggressive)

#### Assets  
- `asset_id` (PK)
- `asset_code` (ISIN/Ticker)
- `asset_name`
- `asset_type` (stock, bond, etf, mutual_fund)
- `sector`
- `country`

#### Transactions
- `transaction_id` (PK)
- `portfolio_id` (FK)
- `asset_id` (FK)
- `transaction_type` (buy, sell, dividend, interest)
- `transaction_date`
- `quantity`
- `price`
- `net_amount`

#### MarketData
- `asset_id` (FK)
- `price_date`
- `close_price`
- `volume`

### Tablas de Análisis

#### Performance
- `portfolio_id` (FK)
- `calculation_date`
- `total_return`
- `volatility`
- `sharpe_ratio`
- `max_drawdown`

#### CashFlows
- `portfolio_id` (FK)
- `flow_date`
- `flow_type` (inflow, outflow, dividend)
- `amount`

## 🧠 Análisis IA y KPIs

### Análisis de Correlaciones

```python
# Ejemplo de uso del servicio de análisis
from app.analysis import InvestmentAnalysisService

analysis_service = InvestmentAnalysisService(db_manager)

correlations = await analysis_service.analyze_portfolio_correlations(
    portfolio_ids=[1, 2, 3],
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31)
)
```

### KPIs Calculados

#### Rendimiento
- **Total Return**: Rentabilidad total del período
- **Annualized Return**: Rentabilidad anualizada
- **Cumulative Return**: Rentabilidad acumulada

#### Riesgo
- **Volatility**: Desviación estándar anualizada
- **Sharpe Ratio**: Rentabilidad ajustada por riesgo
- **Maximum Drawdown**: Máxima caída desde máximo
- **VaR 95%/99%**: Value at Risk

#### Valuación
- **Current Value**: Valor actual de mercado
- **Unrealized P&L**: Ganancia/pérdida no realizada
- **Book Value**: Valor en libros

#### Liquidez
- **Liquidity Score**: Puntuación de liquidez (0-1)
- **Liquid Positions %**: Porcentaje en posiciones líquidas

#### Allocation
- **Asset Allocation**: Distribución por tipo de activo
- **Sector Allocation**: Distribución sectorial  
- **Concentration Risk**: Riesgo de concentración
- **Diversification Score**: Puntuación de diversificación

### Insights Generados

1. **High Correlation Warning**: Correlaciones altas entre activos
2. **Diversification Opportunities**: Oportunidades de diversificación
3. **Asset Clustering**: Patrones de comportamiento de activos
4. **Market Regime Analysis**: Análisis de régimen de mercado

## 🚀 APIs Disponibles

### Endpoints Principales

#### Portfolios
- `GET /api/v1/portfolios/` - Lista portfolios
- `GET /api/v1/portfolios/{id}` - Portfolio específico
- `GET /api/v1/portfolios/{id}/summary` - Resumen con métricas
- `GET /api/v1/portfolios/{id}/positions` - Posiciones actuales

#### Analysis  
- `POST /api/v1/analysis/correlations` - Análisis de correlaciones
- `GET /api/v1/analysis/insights/{id}` - Insights de IA
- `POST /api/v1/analysis/performance` - Análisis de rendimiento

#### KPIs
- `GET /api/v1/kpis/dashboard` - Dashboard de KPIs
- `POST /api/v1/kpis/calculate` - Calcular KPIs específicos
- `GET /api/v1/kpis/{portfolio_id}` - KPIs de portfolio

#### Exports
- `POST /api/v1/exports/powerbi` - Exportar a Power BI
- `POST /api/v1/exports/excel` - Exportar a Excel
- `POST /api/v1/exports/python-chart` - Generar gráficos

#### Health
- `GET /api/v1/health/` - Estado del sistema
- `GET /api/v1/health/database` - Estado de BD
- `POST /api/v1/health/tables/{name}/toggle` - Activar/desactivar tabla

### Ejemplo de Request

```python
import httpx

# Obtener análisis de correlaciones
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/analysis/correlations",
        json={
            "analysis_type": "correlation",
            "portfolio_ids": [1, 2, 3],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }
    )
    correlations = response.json()
```

## 📤 Exportación a Herramientas BI

### Power BI

```python
# Exportar datos para Power BI
export_result = await export_service.export_to_powerbi(
    portfolio_ids=[1, 2],
    data_types=["portfolios", "kpis", "transactions"],
    export_format="json"
)
```

### Data Studio

```python
# Exportar para Google Data Studio  
export_result = await export_service.export_to_datastudio(
    portfolio_ids=[1, 2],
    data_types=["portfolios", "performance"]
)
```

### Excel

```python
# Exportar reporte Excel completo
export_result = await export_service.export_to_excel(
    portfolio_ids=[1, 2, 3],
    data_types=["portfolios", "transactions", "kpis", "positions"],
    include_charts=True
)
```

## 🔒 Seguridad y Buenas Prácticas

### Seguridad de Datos Financieros

1. **Encriptación**: Credenciales encriptadas en variables ambiente
2. **Validación SQL**: Prevención de inyección SQL con parámetros
3. **Auditoría**: Logging completo de operaciones financieras
4. **Autenticación**: JWT tokens para APIs (opcional)

### Logging Estructurado

```python
from app.core.logging_config import log_financial_operation

# Log operaciones financieras
log_financial_operation(
    logger,
    "portfolio_creation",
    portfolio_id="P001",
    amount=100000.0,
    currency="USD"
)
```

### Manejo de Errores

- Validación de datos de entrada
- Manejo graceful de errores de BD
- Logging detallado de errores
- Respuestas de error consistentes

## 🧪 Testing

### Tests Unitarios

```python
# Ejemplo de test
import pytest
from app.services import InvestmentDataService

@pytest.mark.asyncio
async def test_portfolio_kpis():
    service = InvestmentDataService()
    await service.initialize()
    
    kpis = await service.kpi_service.calculate_portfolio_kpis(
        portfolio_id=1
    )
    
    assert "total_return" in kpis["kpis"]
    assert "sharpe_ratio" in kpis["kpis"]
```

### Tests de Integración

```bash
# Ejecutar tests
pytest tests/ -v --cov=app
```

## 🔧 Monitoreo y Mantenimiento

### Health Checks

- Verificación de conexión BD
- Estado de tablas activas
- Monitoreo de servicios externos
- Métricas de rendimiento

### Performance

- Connection pooling para SQL Server
- Caching de consultas frecuentes
- Paginación en endpoints
- Análisis asíncrono para grandes datasets

### Escalabilidad

- Servicios independientes y modulares
- Cache distribuido (Redis) para producción
- Background tasks para análisis pesados
- Horizontal scaling con load balancers

## 📋 Roadmap de Desarrollo

### Fase 1 ✅ (Completada)
- [x] Arquitectura del sistema
- [x] Conexión a base de datos
- [x] APIs básicas
- [x] Análisis de correlaciones
- [x] KPIs fundamentales
- [x] Exportación básica

### Fase 2 (Próximamente)
- [ ] Dashboard web interactivo
- [ ] Alertas automáticas
- [ ] Análisis predictivo con ML
- [ ] Integración tiempo real
- [ ] API de recomendaciones

### Fase 3 (Futuro)
- [ ] Mobile app
- [ ] Blockchain integration
- [ ] Advanced ML models
- [ ] Multi-tenancy
- [ ] Cloud deployment

## 🤝 Contribución

### Estructura de Commits

```bash
git commit -m "feat(analysis): add advanced correlation analysis"
git commit -m "fix(database): resolve connection pooling issue" 
git commit -m "docs(api): update endpoint documentation"
```

### Pull Request Process

1. Fork del repositorio
2. Crear feature branch
3. Implementar cambios con tests
4. Actualizar documentación
5. Submit PR con descripción detallada

## 📞 Soporte

Para soporte técnico o preguntas:

- **Documentación**: [./docs/](./docs/)
- **Issues**: [GitHub Issues](./issues)
- **Email**: dev-team@investment-agent.com

---

*Investment Data Analysis Agent - Transformando datos financieros en insights inteligentes* 🏦📊✨