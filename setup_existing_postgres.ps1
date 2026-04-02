# =============================================================================
# Script para configurar las tablas de analytics en tu contenedor existente
# Contenedor: postgres-learn (Windows PowerShell)
# =============================================================================

Write-Host "🔧 Configurando tablas de analytics en tu contenedor postgres-learn..." -ForegroundColor Blue

# Verificar que el contenedor esté corriendo
$containerRunning = docker ps --format "table {{.Names}}" | Select-String "postgres-learn"

if (-not $containerRunning) {
    Write-Host "❌ Error: El contenedor postgres-learn no está corriendo." -ForegroundColor Red
    Write-Host "Iniciarlo con: docker start postgres-learn" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Contenedor postgres-learn está corriendo" -ForegroundColor Green

# Crear las tablas de analytics
Write-Host "📊 Creando tablas de analytics..." -ForegroundColor Blue

# Script SQL para crear las tablas
$sqlScript = @'
-- =====================================================
-- ANALYTICS TABLES - RESULTADOS DE ANÁLISIS
-- =====================================================

-- Verificar si las tablas ya existen
DO $$
BEGIN
    -- Solo crear si no existen
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'correlation_analysis') THEN
        
        -- Tabla para resultados de análisis de correlación
        CREATE TABLE correlation_analysis (
            id SERIAL PRIMARY KEY,
            portfolio_ids INTEGER[] NOT NULL,
            analysis_date DATE NOT NULL,
            correlation_matrix JSONB,
            significant_correlations JSONB,
            insights JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Tabla para KPIs calculados
        CREATE TABLE portfolio_kpis (
            id SERIAL PRIMARY KEY,
            portfolio_id INTEGER NOT NULL,
            calculation_date DATE NOT NULL,
            kpi_type VARCHAR(50) NOT NULL,
            kpi_value DECIMAL(18,6),
            kpi_details JSONB,
            benchmark_comparison DECIMAL(18,6),
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
            similarity_score DECIMAL(5,4),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Tabla para insights generados por IA
        CREATE TABLE ai_insights (
            id SERIAL PRIMARY KEY,
            portfolio_id INTEGER,
            insight_type VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            importance VARCHAR(20) NOT NULL CHECK (importance IN ('low', 'medium', 'high', 'critical')),
            recommendation TEXT,
            confidence DECIMAL(3,2) CHECK (confidence BETWEEN 0 AND 1),
            supporting_data JSONB,
            action_required BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Tabla para logs de exportación
        CREATE TABLE export_logs (
            id SERIAL PRIMARY KEY,
            export_type VARCHAR(50) NOT NULL,
            format VARCHAR(20) NOT NULL,
            portfolio_ids INTEGER[] NOT NULL,
            file_path TEXT,
            file_size_mb DECIMAL(8,2),
            record_count INTEGER,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            error_message TEXT,
            execution_time_seconds DECIMAL(8,2),
            created_at TIMESTAMP DEFAULT NOW(),
            completed_at TIMESTAMP
        );

        -- Tabla para configuración de tablas activas
        CREATE TABLE table_configuration (
            id SERIAL PRIMARY KEY,
            table_name VARCHAR(100) UNIQUE NOT NULL,
            source_table VARCHAR(100),
            is_active BOOLEAN DEFAULT true,
            analysis_priority INTEGER DEFAULT 1,
            refresh_frequency VARCHAR(20) DEFAULT 'daily',
            last_sync TIMESTAMP,
            description TEXT,
            sync_query TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Tabla para análisis de rendimiento temporal
        CREATE TABLE performance_analysis (
            id SERIAL PRIMARY KEY,
            portfolio_id INTEGER NOT NULL,
            analysis_period VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_return DECIMAL(10,6),
            annualized_return DECIMAL(10,6),
            volatility DECIMAL(10,6),
            max_drawdown DECIMAL(10,6),
            sharpe_ratio DECIMAL(10,6),
            beta DECIMAL(10,6),
            alpha DECIMAL(10,6),  
            sortino_ratio DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Tabla para alertas automáticas
        CREATE TABLE automated_alerts (
            id SERIAL PRIMARY KEY,
            alert_type VARCHAR(50) NOT NULL,
            portfolio_id INTEGER,
            threshold_value DECIMAL(18,6),
            current_value DECIMAL(18,6),
            severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
            message TEXT NOT NULL,
            is_resolved BOOLEAN DEFAULT false,
            resolved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Crear índices
        CREATE INDEX idx_correlation_analysis_date ON correlation_analysis(analysis_date);
        CREATE INDEX idx_portfolio_kpis_portfolio_date ON portfolio_kpis(portfolio_id, calculation_date);
        CREATE INDEX idx_ai_insights_portfolio ON ai_insights(portfolio_id);
        CREATE INDEX idx_export_logs_created_at ON export_logs(created_at);

        -- Configuración inicial
        INSERT INTO table_configuration (table_name, is_active, analysis_priority, description) VALUES
        ('portfolios', true, 1, 'Portfolio master data'),
        ('transactions', true, 1, 'Transaction details'),
        ('assets', true, 1, 'Asset master data'),
        ('market_data', true, 2, 'Historical price data'),
        ('cash_flows', true, 2, 'Cash flow records');

        RAISE NOTICE '✅ Tablas de analytics creadas exitosamente en postgres-learn!';
        
    ELSE
        RAISE NOTICE '⚠️ Las tablas de analytics ya existen en la BD learning';
    END IF;
END $$;

-- Verificar tablas creadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
  AND table_name IN (
    'correlation_analysis', 
    'portfolio_kpis', 
    'asset_clusters', 
    'ai_insights', 
    'export_logs', 
    'table_configuration'
  )
ORDER BY table_name;
'@

# Ejecutar el script SQL
try {
    $sqlScript | docker exec -i postgres-learn psql -U admin -d learning

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 ¡Configuración completada exitosamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Tu configuración actual:" -ForegroundColor Blue
        Write-Host "Contenedor: postgres-learn"
        Write-Host "Host: localhost:5432"
        Write-Host "Database: learning"
        Write-Host "User: admin"
        Write-Host "Password: password123"
        Write-Host ""
        Write-Host "🚀 Próximos pasos:" -ForegroundColor Yellow
        Write-Host "1. Copiar .env.example a .env: Copy-Item .env.example .env"
        Write-Host "2. Editar .env con tus datos de BD origen"
        Write-Host "3. Ejecutar la app: python -m uvicorn app.main:app --reload"
        Write-Host ""
        Write-Host "🔍 Para verificar las tablas:" -ForegroundColor Cyan
        Write-Host "docker exec -it postgres-learn psql -U admin -d learning -c `"\dt`""
    } else {
        throw "Error ejecutando SQL"
    }
} catch {
    Write-Host "❌ Error configurando las tablas: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Verificar que el contenedor esté accesible." -ForegroundColor Yellow
    exit 1
}