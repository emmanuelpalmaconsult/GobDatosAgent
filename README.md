# 🏦 Investment Data Analysis Agent

**Production-Ready** Business Intelligence Investment Data Analysis Agent with AI-powered insights and PowerBI integration.

## 🎯 System Overview

Advanced investment analytics platform analyzing **55 active funds** with **$669+ billion AUM**, providing real-time insights through AI analysis and interactive PowerBI dashboards with 4-level drill-down capabilities.

## ✨ Key Features

- **🤖 AI Analysis**: Intelligent insights from 55+ active investment funds
- **📊 PowerBI Integration**: 4-level drill-down dashboard with executive overview
- **🔍 Real-time Analytics**: Live performance metrics, risk analysis, and P&L tracking  
- **💾 Dual Database**: SQL Server source + PostgreSQL analytics
- **📈 Multi-Platform**: PowerBI, Python charts, and Data Studio ready
- **⚡ High Performance**: Optimized endpoints for large datasets

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │    │   SQL Server    │    │  AI Analysis    │
│   Backend       │◄──►│  SANWS017:1433  │◄──►│   Engine        │
│   Port: 8000    │    │   GD_EG_001     │    │  55 Funds       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PowerBI       │    │  PostgreSQL     │    │   KPI Engine    │
│   Dashboard     │    │  (Analytics)    │    │  Real-time      │
│  4-Level Drill  │    │  localhost:5432 │    │  Metrics        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. **System Startup**
```bash
python start_system.py
```

### 2. **Test Dashboard Integration**
```bash
python test_powerbi_integration.py
```

### 3. **Access API Documentation**
```
http://localhost:8000/docs
```

## 📊 PowerBI Dashboard

### **4-Level Drill-Down Architecture**

1. **📈 Level 1 - Executive Overview**
   - All 55 active funds summary
   - Total AUM: $669+ billion
   - Performance scatter plot
   - Risk analysis matrix

2. **🎯 Level 2 - Fund Details**
   - Historical NAV evolution
   - Performance metrics
   - Asset allocation
   - Risk indicators

3. **💼 Level 3 - Position Analysis**
   - Individual holdings
   - Asset class breakdown
   - P&L by position
   - Concentration analysis

4. **📊 Level 4 - KPI Summary**
   - Consolidated metrics
   - Performance benchmarks
   - Risk-adjusted returns
   - Portfolio statistics

### **PowerBI Endpoints**
```
Overview:    /dashboard/overview
Fund Detail: /dashboard/fund/{id}
Positions:   /dashboard/fund/{id}/positions  
KPIs:        /dashboard/kpis/summary
Comparison:  /dashboard/compare/performance
```

## 🖥️ API Endpoints

### **Data Extraction**
| Endpoint | Description | Method |
|----------|-------------|---------|
| `/dashboard/overview` | Fund overview with 55 active funds | GET |
| `/dashboard/fund/{id}` | Historical fund performance | GET |
| `/dashboard/fund/{id}/positions` | Fund position details | GET |
| `/dashboard/kpis/summary` | Consolidated KPI metrics | GET |
| `/dashboard/compare/performance` | Multi-fund comparison | GET |

### **AI Analysis**
| Endpoint | Description | Method |
|----------|-------------|---------|  
| `/ai/analyze-portfolio/{fund_id}` | AI-powered fund analysis | POST |
| `/ai/generate-insights` | Automated insights generation | POST |
| `/ai/risk-assessment` | Risk analysis with recommendations | POST |

## 🗂️ Project Structure

```
Investment-Data-Analysis-Agent/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   └── dashboard.py        # PowerBI dashboard endpoints
│   ├── database/
│   │   ├── sql_server_manager.py # SQL Server connection
│   │   └── postgres_manager.py   # PostgreSQL analytics
│   ├── models/
│   │   └── investment.py       # Data models
│   └── core/
│       └── config.py           # Configuration management
├── ai_investment_analysis.py   # AI analysis engine
├── start_system.py            # System startup script
├── test_powerbi_integration.py # PowerBI testing
├── POWERBI_INTEGRATION.md     # PowerBI setup guide
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
└── README.md                  # Project documentation
```

## 🔧 Configuration

### **Environment Variables (.env)**
```env
# SQL Server (Data Source)
SQL_SERVER=SANWS017
SQL_PORT=1433
SQL_DATABASE=GD_EG_001
SQL_USERNAME=your_username
SQL_PASSWORD=your_password

# PostgreSQL (Analytics)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=learning
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password123

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=true
```

## 📊 Fund Analysis Results

### **Summary Statistics (55 Active Funds)**
- **Total AUM**: $669+ billion
- **Average YTD Return**: 3.35%
- **Top Performer**: PIONERO (6.60% YTD)
- **Largest Fund**: ORANGE ($510B AUM)
- **Total Positions**: 200+ tracked

### **Key Insights**
- ✅ **Performance**: Strong overall performance with positive YTD
- ✅ **Diversification**: Good spread across asset classes
- ✅ **Risk Management**: Balanced risk profiles across funds
- ✅ **Liquidity**: Adequate cash positions maintained

## 🚀 Technologies

- **Backend**: FastAPI, Python 3.8+
- **Databases**: SQL Server, PostgreSQL  
- **Data Processing**: Pandas, NumPy
- **AI/ML**: Custom analytics engine
- **Visualization**: PowerBI integration ready
- **Authentication**: Environment-based security
- **Deployment**: Docker-ready, localhost development

## 📚 Documentation

- **📊 PowerBI Integration**: `POWERBI_INTEGRATION.md`
- **🔧 API Documentation**: `http://localhost:8000/docs`
- **🧪 Testing Guide**: `test_powerbi_integration.py`
- **🚀 Startup Guide**: `start_system.py`

## 🆘 Troubleshooting

### **Common Issues**

1. **SQL Server Connection**
   ```
   Error: Cannot connect to SANWS017
   Solution: Verify VPN connection and server access
   ```

2. **PowerBI Connection**
   ```
   Error: Data source not found  
   Solution: Ensure FastAPI is running on port 8000
   ```

3. **Missing Dependencies** 
   ```
   Solution: pip install -r requirements.txt
   ```

## 🎯 Next Steps

1. **✅ Production Deployment**: Deploy to cloud infrastructure
2. **✅ Enhanced AI**: Implement advanced predictive models
3. **✅ Real-time Streaming**: Add real-time data feeds
4. **✅ Advanced Security**: Implement authentication layer
5. **✅ Mobile Dashboard**: PowerBI mobile optimization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**🎉 Ready for PowerBI Integration!** 

Use `python start_system.py` to launch the system and follow `POWERBI_INTEGRATION.md` for dashboard setup.

### 🔄 Exportación
- **Power BI**: Datasets y dashboards
- **Data Studio**: Conectores y visualizaciones  
- **Python Charts**: Matplotlib, Plotly, Seaborn
- **Excel Reports**: Reportes automáticos

## 🛠️ Tecnologías

- **Backend**: FastAPI, Python 3.9+
- **Database**: SQL Server, SQLAlchemy
- **AI/ML**: pandas, numpy, scikit-learn
- **Visualization**: matplotlib, plotly, seaborn
- **Export**: openpyxl, python-pptx
- **Security**: python-jose, passlib

## 📦 Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd investment-data-agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar aplicación
python -m uvicorn app.main:app --reload
```

## ⚙️ Configuración

### Variables de Entorno
```env
# SQL Server Configuration
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=InvestmentDB
SQL_SERVER_USERNAME=your_username
SQL_SERVER_PASSWORD=your_password

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Integrations
POWERBI_CLIENT_ID=your-powerbi-client-id
POWERBI_CLIENT_SECRET=your-powerbi-secret
```

## 🔐 Seguridad

- Encriptación de credenciales de BD
- Validación de entrada SQL injection-safe
- Autenticación JWT para APIs
- Logs de auditoría para operaciones financieras

## 📁 Estructura de Datos

### Tablas Principales
- **Portfolios**: Información de carteras
- **CashFlows**: Flujos de efectivo
- **Transactions**: Transacciones detalladas
- **ProfitLoss**: Estados de P&L
- **Assets**: Información de activos
- **Market_Data**: Datos de mercado

## 🚦 Uso

### API Endpoints
- `GET /api/portfolios` - Lista de portfolios
- `POST /api/analysis/correlations` - Análisis de correlaciones
- `GET /api/kpis/{portfolio_id}` - KPIs específicos
- `POST /api/export/powerbi` - Export a Power BI
- `GET /api/insights/summary` - Resumen de insights

### Análisis Disponibles
1. **Rendimiento por Portfolio**
2. **Análisis de Riesgo**
3. **Correlaciones de Activos**
4. **Patrones Estacionales**
5. **Flujo de Caja Proyectado**

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte o preguntas, contacta:
- Email: support@investment-agent.com
- Documentation: [Docs](./docs/)
- Issues: [GitHub Issues](./issues)