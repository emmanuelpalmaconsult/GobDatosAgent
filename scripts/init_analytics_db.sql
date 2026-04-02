-- Investment Data Analysis Agent - Analytics Database Initialization
-- Este script se ejecuta automáticamente al crear el contenedor PostgreSQL

-- =====================================================
-- ANALYTICS TABLES - RESULTADOS DE ANÁLISIS
-- =====================================================

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
    analysis_period VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly, yearly
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

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
-- =====================================================

-- Índices para tablas de análisis
CREATE INDEX idx_correlation_analysis_date ON correlation_analysis(analysis_date);
CREATE INDEX idx_correlation_analysis_portfolios ON correlation_analysis USING GIN(portfolio_ids);

CREATE INDEX idx_portfolio_kpis_portfolio_date ON portfolio_kpis(portfolio_id, calculation_date);
CREATE INDEX idx_portfolio_kpis_type ON portfolio_kpis(kpi_type);
CREATE INDEX idx_portfolio_kpis_date ON portfolio_kpis(calculation_date);

CREATE INDEX idx_asset_clusters_date ON asset_clusters(analysis_date);
CREATE INDEX idx_asset_clusters_id ON asset_clusters(cluster_id);

CREATE INDEX idx_ai_insights_portfolio ON ai_insights(portfolio_id);
CREATE INDEX idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX idx_ai_insights_importance ON ai_insights(importance);
CREATE INDEX idx_ai_insights_created_at ON ai_insights(created_at);

CREATE INDEX idx_export_logs_created_at ON export_logs(created_at);
CREATE INDEX idx_export_logs_status ON export_logs(status);
CREATE INDEX idx_export_logs_type ON export_logs(export_type);

CREATE INDEX idx_performance_analysis_portfolio ON performance_analysis(portfolio_id);
CREATE INDEX idx_performance_analysis_period ON performance_analysis(analysis_period, start_date, end_date);

CREATE INDEX idx_automated_alerts_severity ON automated_alerts(severity);
CREATE INDEX idx_automated_alerts_resolved ON automated_alerts(is_resolved);
CREATE INDEX idx_automated_alerts_portfolio ON automated_alerts(portfolio_id);

-- =====================================================
-- CONFIGURACIÓN INICIAL DE TABLAS
-- =====================================================

-- Insertar configuración inicial de tablas origen comunes
INSERT INTO table_configuration (table_name, source_table, is_active, analysis_priority, description, refresh_frequency) VALUES
('portfolios', 'portfolios', true, 1, 'Portfolio master data - core analysis table', 'hourly'),
('transactions', 'transactions', true, 1, 'Transaction details - primary data source', 'hourly'),
('assets', 'assets', true, 1, 'Asset master data - reference table', 'daily'),
('market_data', 'market_data', true, 2, 'Historical price data for analysis', 'daily'),
('cash_flows', 'cash_flows', true, 2, 'Cash flow records for liquidity analysis', 'daily'),
('portfolio_positions', 'portfolio_positions', true, 1, 'Current positions per portfolio', 'hourly'),
('portfolio_performance', 'portfolio_performance', true, 2, 'Historical performance data', 'daily'),
('benchmarks', 'benchmarks', false, 3, 'Benchmark data for comparison', 'weekly');

-- =====================================================
-- FUNCIONES UTILITARIAS
-- =====================================================

-- Función para limpiar datos antiguos
CREATE OR REPLACE FUNCTION cleanup_old_analytics_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    temp_count INTEGER;
BEGIN
    -- Limpiar análisis de correlación mayores a 1 año
    DELETE FROM correlation_analysis WHERE created_at < NOW() - INTERVAL '1 year';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;

    -- Limpiar logs de exportación mayores a 6 meses
    DELETE FROM export_logs WHERE created_at < NOW() - INTERVAL '6 months';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;

    -- Limpiar insights resueltos mayores a 3 meses
    DELETE FROM ai_insights 
    WHERE created_at < NOW() - INTERVAL '3 months' 
    AND importance IN ('low', 'medium');
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;

    -- Limpiar alertas resueltas mayores a 1 mes
    DELETE FROM automated_alerts 
    WHERE is_resolved = true 
    AND resolved_at < NOW() - INTERVAL '1 month';
    GET DIAGNOSTICS temp_count = ROW_COUNT;
    deleted_count := deleted_count + temp_count;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas de base de datos
CREATE OR REPLACE FUNCTION get_analytics_statistics()
RETURNS TABLE(
    table_name TEXT,
    record_count BIGINT,
    table_size TEXT,
    last_updated TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_name::TEXT,
        COALESCE(c.n_tup_ins - c.n_tup_del, 0) as record_count,
        pg_size_pretty(pg_total_relation_size(t.table_name::regclass)) as table_size,
        GREATEST(
            COALESCE(c.last_analyze, '1970-01-01'::timestamp),
            COALESCE(c.last_autoanalyze, '1970-01-01'::timestamp)
        ) as last_updated
    FROM information_schema.tables t
    LEFT JOIN pg_stat_user_tables c ON c.relname = t.table_name
    WHERE t.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
    ORDER BY record_count DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS PARA AUDITORÍA
-- =====================================================

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a tablas con updated_at
CREATE TRIGGER update_correlation_analysis_updated_at 
    BEFORE UPDATE ON correlation_analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_table_configuration_updated_at 
    BEFORE UPDATE ON table_configuration 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VISTAS ÚTILES PARA REPORTING
-- =====================================================

-- Vista resumen de KPIs por portfolio
CREATE VIEW v_portfolio_kpi_summary AS
SELECT 
    portfolio_id,
    calculation_date,
    COUNT(*) as total_kpis,
    AVG(CASE WHEN kpi_type = 'return' THEN kpi_value END) as avg_return,
    AVG(CASE WHEN kpi_type = 'volatility' THEN kpi_value END) as avg_volatility,
    AVG(CASE WHEN kpi_type = 'sharpe_ratio' THEN kpi_value END) as avg_sharpe_ratio,
    MAX(created_at) as last_calculation
FROM portfolio_kpis
GROUP BY portfolio_id, calculation_date;

-- Vista de alertas activas
CREATE VIEW v_active_alerts AS
SELECT 
    alert_type,
    portfolio_id,
    severity,
    message,
    threshold_value,
    current_value,
    (current_value - threshold_value) as deviation,
    created_at
FROM automated_alerts
WHERE is_resolved = false
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        WHEN 'info' THEN 3
    END,
    created_at DESC;

-- Vista de estadísticas de exportación
CREATE VIEW v_export_statistics AS
SELECT 
    export_type,
    format,
    COUNT(*) as total_exports,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_exports,
    AVG(execution_time_seconds) as avg_execution_time,
    SUM(record_count) as total_records_exported,
    MAX(created_at) as last_export
FROM export_logs
GROUP BY export_type, format;

-- =====================================================
-- PERMISOS Y SEGURIDAD
-- =====================================================

-- Crear rol para aplicación de análisis
CREATE ROLE analytics_app;
GRANT CONNECT ON DATABASE "InvestmentAnalytics" TO analytics_app;
GRANT USAGE ON SCHEMA public TO analytics_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO analytics_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO analytics_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO analytics_app;

-- Crear rol de solo lectura para reportes
CREATE ROLE analytics_readonly;
GRANT CONNECT ON DATABASE "InvestmentAnalytics" TO analytics_readonly;
GRANT USAGE ON SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO analytics_readonly;

-- =====================================================
-- DATOS DE PRUEBA (OPCIONAL - SOLO DESARROLLO)
-- =====================================================

-- Activar solo en desarrollo/testing
-- Descomentar las siguientes líneas para datos de prueba

/*
-- Datos de prueba para table_configuration
UPDATE table_configuration SET last_sync = NOW() WHERE table_name IN ('portfolios', 'transactions');

-- Datos de prueba para insights
INSERT INTO ai_insights (portfolio_id, insight_type, title, description, importance, confidence, recommendation) VALUES
(1, 'risk', 'High Correlation Detected', 'Portfolio shows high correlation between assets A and B (0.85)', 'medium', 0.92, 'Consider diversifying to reduce correlation risk'),
(1, 'performance', 'Underperforming Asset', 'Asset XYZ is underperforming benchmark by 15%', 'high', 0.87, 'Review asset allocation for XYZ'),
(2, 'volatility', 'Increased Volatility', 'Portfolio volatility increased 25% in last month', 'high', 0.91, 'Monitor risk exposure closely');

-- Datos de prueba para alertas
INSERT INTO automated_alerts (alert_type, portfolio_id, threshold_value, current_value, severity, message) VALUES
('volatility', 1, 0.20, 0.28, 'warning', 'Portfolio volatility exceeds threshold of 20%'),
('drawdown', 2, 0.10, 0.15, 'critical', 'Maximum drawdown exceeds 10% limit');
*/

-- =====================================================
-- FINALIZACIÓN
-- =====================================================

-- Crear índice UNIQUE para evitar duplicados en configuración
CREATE UNIQUE INDEX idx_unique_table_config ON table_configuration(table_name);

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Investment Analytics Database initialized successfully!';
    RAISE NOTICE 'Tables created: %, %, %, %, %, %, %, %', 
        'correlation_analysis', 'portfolio_kpis', 'asset_clusters', 'ai_insights',
        'export_logs', 'table_configuration', 'performance_analysis', 'automated_alerts';
    RAISE NOTICE 'Views created: %, %, %',
        'v_portfolio_kpi_summary', 'v_active_alerts', 'v_export_statistics';
    RAISE NOTICE 'Utility functions: cleanup_old_analytics_data(), get_analytics_statistics()';
END $$;