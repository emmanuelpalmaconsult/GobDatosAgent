# Docker Setup para Investment Data Analysis Agent

## 🐳 PostgreSQL Analytics Database (Docker)

### Configuración Rápida

```bash
# NOTA: Ya tienes tu contenedor PostgreSQL corriendo!
# Contenedor: postgres-learn
# No necesitas crear uno nuevo

# Si quisieras crear otro nuevo (OPCIONAL):
# docker run --name investment-analytics \
#   -e POSTGRES_DB=InvestmentAnalytics \
#   -e POSTGRES_USER=analytics_user \
#   -e POSTGRES_PASSWORD=analytics_password \
#   -p 5433:5432 \
#   -d postgres:15

# 2. Verificar que esté ejecutándose
docker ps

# 3. Conectar al contenedor para crear tablas
docker exec -it investment-analytics psql -U analytics_user -d InvestmentAnalytics
```

### Docker Compose (Recomendado)

```yaml
# docker-compose.yml
version: '3.8'
services:
  analytics-db:
    image: postgres:15
    container_name: investment-analytics
    environment:
      POSTGRES_DB: InvestmentAnalytics
      POSTGRES_USER: analytics_user
      POSTGRES_PASSWORD: analytics_password
    ports:
      - "5432:5432"
    volumes:
      - analytics_data:/var/lib/postgresql/data
      - ./scripts/init_analytics_db.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  analytics_data:
```

```bash
# Ejecutar con Docker Compose
docker-compose up -d
```

## 📊 Estructura de Base de Datos Dual

### Arquitectura Recomendada

```
┌─────────────────────┐    Extract    ┌─────────────────────┐
│   SOURCE DATABASE   │ ────────────► │  ANALYTICS DATABASE │
│                     │               │                     │
│ • Portfolios        │               │ • Analysis Results  │
│ • Transactions      │               │ • KPI Calculations  │
│ • Assets            │               │ • Correlation Data  │
│ • Market Data       │               │ • Export Logs       │
│ • Cash Flows        │               │ • Insights          │
└─────────────────────┘               └─────────────────────┘
   (Tu BD Existente)                    (PostgreSQL Docker)
```

### Variables de Entorno (.env)

```bash
# Source Database (tu BD existente)
SOURCE_DB_TYPE=postgresql  # o sqlserver, mysql
SOURCE_DB_HOST=tu-servidor-real
SOURCE_DB_NAME=tu_bd_inversiones
SOURCE_DB_USER=tu_usuario
SOURCE_DB_PASSWORD=tu_password

# Analytics Database (PostgreSQL Docker)
ANALYTICS_DB_HOST=localhost
ANALYTICS_DB_PORT=5432
ANALYTICS_DB_NAME=InvestmentAnalytics
ANALYTICS_DB_USER=analytics_user
ANALYTICS_DB_PASSWORD=analytics_password
```

## 🔧 Configuración de Tablas de Análisis

### Script de Inicialización

```sql
-- scripts/init_analytics_db.sql

-- Tabla para resultados de análisis de correlación
CREATE TABLE correlation_analysis (
    id SERIAL PRIMARY KEY,
    portfolio_ids INTEGER[] NOT NULL,
    analysis_date DATE NOT NULL,
    correlation_matrix JSONB,
    significant_correlations JSONB,
    insights JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para KPIs calculados
CREATE TABLE portfolio_kpis (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    calculation_date DATE NOT NULL,
    kpi_type VARCHAR(50) NOT NULL,
    kpi_value DECIMAL(18,6),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para resultados de clustering
CREATE TABLE asset_clusters (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL,
    cluster_id INTEGER NOT NULL,
    asset_codes TEXT[] NOT NULL,
    cluster_characteristics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para insights generados
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    importance VARCHAR(20) NOT NULL,
    recommendation TEXT,
    confidence DECIMAL(3,2),
    supporting_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para logs de exportación
CREATE TABLE export_logs (
    id SERIAL PRIMARY KEY,
    export_type VARCHAR(50) NOT NULL,
    portfolio_ids INTEGER[] NOT NULL,
    file_path TEXT,
    record_count INTEGER,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla para configuración de tablas activas
CREATE TABLE table_configuration (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    analysis_priority INTEGER DEFAULT 1,
    refresh_frequency VARCHAR(20) DEFAULT 'daily',
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX idx_correlation_analysis_date ON correlation_analysis(analysis_date);
CREATE INDEX idx_portfolio_kpis_portfolio_date ON portfolio_kpis(portfolio_id, calculation_date);
CREATE INDEX idx_ai_insights_portfolio ON ai_insights(portfolio_id);
CREATE INDEX idx_export_logs_created_at ON export_logs(created_at);

-- Insertar configuración inicial de tablas
INSERT INTO table_configuration (table_name, is_active, analysis_priority, description) VALUES
('portfolios', true, 1, 'Portfolio master data'),
('transactions', true, 1, 'Transaction details'),
('assets', true, 1, 'Asset master data'),
('market_data', true, 2, 'Historical price data'),
('cash_flows', true, 2, 'Cash flow records');
```

## 🚀 Pasos de Configuración

### 1. Ejecutar PostgreSQL en Docker

```bash
# Opción A: Docker run directo
docker run --name investment-analytics \
  -e POSTGRES_DB=InvestmentAnalytics \
  -e POSTGRES_USER=analytics_user \
  -e POSTGRES_PASSWORD=analytics_password \
  -p 5432:5432 \
  -v $(pwd)/scripts/init_analytics_db.sql:/docker-entrypoint-initdb.d/init.sql \
  -d postgres:15

# Opción B: Docker Compose (recomendado)
docker-compose up -d
```

### 2. Verificar Conexión

```bash
# Verificar que el contenedor esté corriendo
docker ps

# Conectar y verificar tablas
docker exec -it investment-analytics psql -U analytics_user -d InvestmentAnalytics -c "\\dt"
```

### 3. Configurar Variables de Entorno

```bash
# Copiar template y editar
cp .env.example .env
# Editar .env con tus credenciales reales
```

### 4. Ejecutar la Aplicación

```bash
# Instalar dependencias (incluye psycopg2)
pip install -r requirements.txt

# Ejecutar aplicación
python -m uvicorn app.main:app --reload
```

### 5. Verificar Conexiones Duales

```bash
# Verificar estado de ambas bases de datos
curl http://localhost:8000/api/v1/health/database
```

## 🔍 Monitoreo y Mantenimiento

### Verificar Logs del Contenedor

```bash
docker logs investment-analytics
```

### Backup de Analytics DB

```bash
# Crear backup
docker exec investment-analytics pg_dump -U analytics_user InvestmentAnalytics > backup_analytics.sql

# Restaurar backup
docker exec -i investment-analytics psql -U analytics_user -d InvestmentAnalytics < backup_analytics.sql
```

### Parar y Reiniciar

```bash
# Parar contenedor
docker stop investment-analytics

# Iniciar contenedor
docker start investment-analytics

# Reiniciar completamente
docker-compose restart
```

## 💡 Ventajas de esta Arquitectura

✅ **Separación de Responsabilidades**
- BD Origen: Solo lectura de datos existentes
- BD Analytics: Almacena resultados y análisis

✅ **No Impacto en BD Productiva**
- No modificas tu base de datos existente
- Análisis en ambiente aislado

✅ **Escalabilidad**
- PostgreSQL optimizado para analytics
- Fácil backup de resultados

✅ **Flexibilidad**
- Soporta cualquier tipo de BD origen
- Resultado siempre en formato estándar

✅ **Docker Benefits**
- Instalación rápida y portable
- Aislamiento completo
- Fácil mantenimiento