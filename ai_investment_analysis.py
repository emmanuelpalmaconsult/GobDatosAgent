#!/usr/bin/env python3
"""
Sistema de Análisis IA para Investment Data Analysis Agent
Enfocado en fondos activos de GD_Fondos donde FN_Activo = 1
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import urllib.parse
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_sql_server_engine():
    """Crear conexión a SQL Server"""
    password = urllib.parse.quote_plus(settings.SOURCE_DB_PASSWORD)
    
    connection_string = (
        f"mssql+pyodbc://{settings.SOURCE_DB_USER}:{password}@"
        f"{settings.SOURCE_DB_HOST}:{settings.SOURCE_DB_PORT}/"
        f"{settings.SOURCE_DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&"
        f"Encrypt=yes&TrustServerCertificate=yes"
    )
    
    return create_engine(connection_string)

def get_active_funds(engine):
    """Obtener fondos activos de GD_Fondos donde FN_Activo = 1"""
    
    print("🔍 CONSULTANDO FONDOS ACTIVOS")
    print("=" * 60)
    
    try:
        # Consultar fondos activos con estructura real de la tabla
        query = """
        SELECT 
            PshipID,
            Portfolio,
            FN_Activo as IsActive
        FROM [GD_EG_001].[dbo].[GD_Fondos] 
        WHERE FN_Activo = 1
        ORDER BY Portfolio
        """
        
        df_funds = pd.read_sql(query, engine)
        
        print(f"📊 FONDOS ACTIVOS ENCONTRADOS: {len(df_funds)}")
        print("-" * 60)
        
        # Mostrar tabla de fondos activos
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 30)
        
        print(df_funds.to_string(index=False))
        
        print(f"\n🎯 FUND IDs PARA ANÁLISIS: {df_funds['PshipID'].tolist()}")
        print(f"📋 PORTFOLIOS: {df_funds['Portfolio'].tolist()}")
        
        return df_funds
        
    except Exception as e:
        print(f"❌ Error consultando fondos activos: {e}")
        return pd.DataFrame()

def analyze_portfolio_performance(engine, fund_ids, analysis_date='2026-03-31'):
    """Análisis de performance para fondos activos"""
    
    print(f"\n📈 ANÁLISIS DE PERFORMANCE - {analysis_date}")
    print("=" * 80)
    
    try:
        # Consulta principal de performance usando Unit Appraisal
        fund_ids_str = ','.join(map(str, [int(x) for x in fund_ids]))
        query = f"""
        SELECT TOP 500
            u.PshipID,
            u.Portfolio,
            u.Fecha,
            u.NAV,
            u.Shares,
            u.NetEndCap,
            u.PeriodIRR,
            u.PeriodRangeTWR,
            u.YTDTWR,
            u.SITWR,
            u.ReportingCurrencyCode,
            u.BegCapChanges,
            u.EndCapChanges
        FROM [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u
        WHERE u.PshipID IN ({fund_ids_str})
        AND u.Fecha >= DATEADD(MONTH, -12, CAST('{analysis_date}' AS DATE))
        ORDER BY u.PshipID, u.Fecha DESC
        """
        
        df_performance = pd.read_sql(query, engine)
        
        if df_performance.empty:
            print("⚠️ No hay datos de performance disponibles")
            return pd.DataFrame()
        
        print(f"📊 REGISTROS DE PERFORMANCE: {len(df_performance)}")
        
        # Análisis por fondo
        performance_summary = []
        
        for fund_id in df_performance['PshipID'].unique():
            fund_data = df_performance[df_performance['PshipID'] == fund_id].copy()
            fund_data = fund_data.sort_values('Fecha')
            
            if len(fund_data) == 0:
                continue
            
            latest = fund_data.iloc[-1]
            
            # Calcular métricas
            avg_nav = fund_data['NAV'].mean() if not fund_data['NAV'].isna().all() else 0
            total_assets = latest['NetEndCap'] if pd.notna(latest['NetEndCap']) else 0
            ytd_return = latest['YTDTWR'] if pd.notna(latest['YTDTWR']) else 0
            period_irr = latest['PeriodIRR'] if pd.notna(latest['PeriodIRR']) else 0
            
            performance_summary.append({
                'PshipID': fund_id,
                'Portfolio': latest['Portfolio'],
                'Currency': latest['ReportingCurrencyCode'],
                'Latest_NAV': latest['NAV'],
                'Total_Assets': total_assets,
                'YTD_Return': ytd_return,
                'Period_IRR': period_irr,
                'Data_Points': len(fund_data),
                'Latest_Date': latest['Fecha']
            })
        
        df_summary = pd.DataFrame(performance_summary)
        
        print("\n🎯 RESUMEN DE PERFORMANCE POR FONDO:")
        print("-" * 80)
        print(df_summary.to_string(index=False))
        
        return df_summary
        
    except Exception as e:
        print(f"❌ Error en análisis de performance: {e}")
        return pd.DataFrame()

def analyze_positions_composition(engine, fund_ids, analysis_date='2026-03-31'):
    """Análisis de composición de posiciones"""
    
    print(f"\n🎯 ANÁLISIS DE COMPOSICIÓN DE POSICIONES - {analysis_date}")
    print("=" * 80)
    
    try:
        # Consultar posiciones actuales - usando solo columnas que existen
        fund_ids_str = ','.join(map(str, [int(x) for x in fund_ids]))
        query = f"""
        SELECT TOP 200
            p.PshipID,
            p.Portfolio,
            p.Fecha,
            p.LSDesc,
            p.InvestID,
            p.CostLocal,
            p.CostBook,
            p.MVBook,
            p.UnRealGL,
            p.PercentInvest,
            p.ReportMode
        FROM [GD_EG_001].[dbo].[GD_R_InvestmentPosition] p
        WHERE p.PshipID IN ({fund_ids_str})
        AND p.Fecha = CAST('{analysis_date}' AS DATE)
        AND ABS(p.MVBook) > 1000  -- Solo posiciones significativas
        ORDER BY p.PshipID, ABS(p.MVBook) DESC
        """
        
        df_positions = pd.read_sql(query, engine)
        
        if df_positions.empty:
            print("⚠️ No hay datos de posiciones disponibles")
            return {}
        
        print(f"📊 POSICIONES ANALIZADAS: {len(df_positions)}")
        
        analysis_results = {}
        
        # Análisis por fondo
        for fund_id in df_positions['PshipID'].unique():
            fund_positions = df_positions[df_positions['PshipID'] == fund_id].copy()
            fund_name = fund_positions['Portfolio'].iloc[0]
            
            # Métricas del fondo
            total_mv = fund_positions['MVBook'].sum()
            total_cost = fund_positions['CostBook'].sum()
            total_unrealized = fund_positions['UnRealGL'].sum()
            
            # Análisis por asset class
            asset_allocation = fund_positions.groupby('ReportMode').agg({
                'MVBook': ['sum', 'count'],
                'UnRealGL': 'sum'
            }).round(2)
            
            # Top posiciones
            top_positions = fund_positions.nlargest(5, 'MVBook')[
                ['LSDesc', 'InvestID', 'MVBook', 'PercentInvest', 'UnRealGL']
            ]
            
            analysis_results[fund_id] = {
                'fund_name': fund_name,
                'total_market_value': total_mv,
                'total_cost': total_cost,
                'total_unrealized_gl': total_unrealized,
                'asset_allocation': asset_allocation,
                'top_positions': top_positions,
                'position_count': len(fund_positions)
            }
        
        # Mostrar resultados
        for fund_id, data in analysis_results.items():
            print(f"\n🏢 FONDO: {data['fund_name']} (ID: {fund_id})")
            print("-" * 60)
            print(f"💰 Market Value Total: ${data['total_market_value']:,.2f}")
            print(f"💳 Costo Total: ${data['total_cost']:,.2f}")
            print(f"📊 P&L No Realizada: ${data['total_unrealized_gl']:,.2f}")
            print(f"🎯 Número de Posiciones: {data['position_count']}")
            
            print(f"\n📈 TOP 5 POSICIONES:")
            if not data['top_positions'].empty:
                print(data['top_positions'].to_string(index=False))
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error en análisis de posiciones: {e}")
        return {}

def calculate_risk_metrics(engine, fund_ids):
    """Calcular métricas de riesgo usando datos históricos"""
    
    print(f"\n⚠️ ANÁLISIS DE RIESGO")
    print("=" * 80)
    
    try:
        # Consultar datos históricos para cálculo de volatilidad
        fund_ids_str = ','.join(map(str, [int(x) for x in fund_ids]))
        query = f"""
        SELECT 
            u.PshipID,
            u.Portfolio,
            u.Fecha,
            u.NAV,
            u.PeriodRangeTWR,
            u.NetEndCap
        FROM [GD_EG_001].[dbo].[GD_R_Unit_Appraisal_Series_Hist] u
        WHERE u.PshipID IN ({fund_ids_str})
        AND u.Fecha >= DATEADD(MONTH, -24, GETDATE())
        AND u.NAV IS NOT NULL
        ORDER BY u.PshipID, u.Fecha
        """
        
        df_history = pd.read_sql(query, engine)
        
        if df_history.empty:
            print("⚠️ No hay suficiente data histórica para análisis de riesgo")
            return {}
        
        print(f"📊 PUNTOS DE DATA HISTÓRICA: {len(df_history)}")
        
        risk_metrics = {}
        
        for fund_id in df_history['PshipID'].unique():
            fund_data = df_history[df_history['PshipID'] == fund_id].copy()
            fund_data = fund_data.sort_values('Fecha')
            
            if len(fund_data) < 12:  # Necesitamos al menos 12 puntos
                continue
            
            fund_name = fund_data['Portfolio'].iloc[0]
            
            # Calcular retornos
            fund_data['nav_return'] = fund_data['NAV'].pct_change()
            fund_data['twr_return'] = fund_data['PeriodRangeTWR'] / 100
            
            # Métricas de riesgo
            nav_volatility = fund_data['nav_return'].std() * np.sqrt(252) if not fund_data['nav_return'].isna().all() else 0
            avg_return = fund_data['twr_return'].mean() if not fund_data['twr_return'].isna().all() else 0
            return_volatility = fund_data['twr_return'].std() if not fund_data['twr_return'].isna().all() else 0
            
            # Sharpe Ratio simplificado (asumiendo risk-free rate = 2%)
            risk_free_rate = 0.02
            sharpe_ratio = (avg_return - risk_free_rate/252) / return_volatility if return_volatility > 0 else 0
            
            # Drawdown máximo
            nav_series = fund_data['NAV'].dropna()
            if len(nav_series) > 1:
                peak = nav_series.cummax()
                drawdown = (nav_series - peak) / peak
                max_drawdown = drawdown.min()
            else:
                max_drawdown = 0
            
            risk_metrics[fund_id] = {
                'fund_name': fund_name,
                'data_points': len(fund_data),
                'nav_volatility_annualized': nav_volatility,
                'average_return': avg_return,
                'return_volatility': return_volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'current_nav': fund_data['NAV'].iloc[-1],
                'latest_assets': fund_data['NetEndCap'].iloc[-1]
            }
        
        # Mostrar resultados
        print("\n📊 MÉTRICAS DE RIESGO POR FONDO:")
        print("-" * 80)
        
        for fund_id, metrics in risk_metrics.items():
            print(f"\n🏢 {metrics['fund_name']} (ID: {fund_id})")
            print(f"  📈 NAV Volatilidad (Anualizada): {metrics['nav_volatility_annualized']:.2%}")
            print(f"  💹 Retorno Promedio: {metrics['average_return']:.2%}")
            print(f"  ⚡ Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
            print(f"  📉 Max Drawdown: {metrics['max_drawdown']:.2%}")
            print(f"  👥 Puntos de Data: {metrics['data_points']}")
        
        return risk_metrics
        
    except Exception as e:
        print(f"❌ Error en análisis de riesgo: {e}")
        return {}

def generate_ai_insights(performance_data, positions_data, risk_data):
    """Generar insights automáticos usando IA"""
    
    print(f"\n🤖 GENERANDO INSIGHTS AUTOMÁTICOS CON IA")
    print("=" * 80)
    
    insights = []
    
    try:
        # Análisis de performance
        if not performance_data.empty:
            # Top performers
            top_ytd = performance_data.nlargest(3, 'YTD_Return')
            bottom_ytd = performance_data.nsmallest(3, 'YTD_Return')
            
            insights.append("📈 PERFORMANCE INSIGHTS:")
            insights.append(f"  🥇 Mejor YTD: {top_ytd.iloc[0]['Portfolio']} ({top_ytd.iloc[0]['YTD_Return']:.2%})")
            insights.append(f"  📉 Menor YTD: {bottom_ytd.iloc[0]['Portfolio']} ({bottom_ytd.iloc[0]['YTD_Return']:.2%})")
            
            # Assets bajo gestión
            total_aum = performance_data['Total_Assets'].sum()
            largest_fund = performance_data.loc[performance_data['Total_Assets'].idxmax()]
            
            insights.append(f"\n💰 ASSETS UNDER MANAGEMENT:")
            insights.append(f"  🏦 AUM Total: ${total_aum:,.0f}")
            insights.append(f"  🏢 Fondo Más Grande: {largest_fund['Portfolio']} (${largest_fund['Total_Assets']:,.0f})")
        
        # Análisis de riesgo
        if risk_data:
            best_sharpe = max(risk_data.values(), key=lambda x: x['sharpe_ratio'])
            worst_drawdown = min(risk_data.values(), key=lambda x: x['max_drawdown'])
            
            insights.append(f"\n⚠️ RISK INSIGHTS:")
            insights.append(f"  📊 Mejor Sharpe Ratio: {best_sharpe['fund_name']} ({best_sharpe['sharpe_ratio']:.3f})")
            insights.append(f"  📉 Mayor Drawdown: {worst_drawdown['fund_name']} ({worst_drawdown['max_drawdown']:.2%})")
        
        # Análisis de diversificación
        if positions_data:
            avg_positions = np.mean([data['position_count'] for data in positions_data.values()])
            most_diversified = max(positions_data.values(), key=lambda x: x['position_count'])
            
            insights.append(f"\n🎯 DIVERSIFICATION INSIGHTS:")
            insights.append(f"  📊 Posiciones Promedio: {avg_positions:.0f}")
            insights.append(f"  🌍 Más Diversificado: {most_diversified['fund_name']} ({most_diversified['position_count']} posiciones)")
        
        # Recomendaciones automáticas
        insights.append(f"\n🚀 RECOMENDACIONES IA:")
        insights.append("  📈 Monitorear fondos con Sharpe ratio < 0.5")
        insights.append("  ⚠️ Revisar fondos con drawdown > -15%")
        insights.append("  💡 Considerar rebalanceo para fondos con <10 posiciones")
        insights.append("  📊 Implementar stop-loss automático en fondos volátiles")
        
        # Mostrar insights
        for insight in insights:
            print(insight)
        
        return insights
        
    except Exception as e:
        print(f"❌ Error generando insights: {e}")
        return []

def create_investment_kpis(performance_data, positions_data, risk_data):
    """Crear KPIs consolidados para dashboard"""
    
    print(f"\n📊 GENERANDO KPIs PARA DASHBOARD")
    print("=" * 80)
    
    kpis = {}
    
    try:
        # KPIs de Performance
        if not performance_data.empty:
            kpis['performance'] = {
                'total_funds': len(performance_data),
                'total_aum': performance_data['Total_Assets'].sum(),
                'avg_ytd_return': performance_data['YTD_Return'].mean(),
                'best_ytd_return': performance_data['YTD_Return'].max(),
                'worst_ytd_return': performance_data['YTD_Return'].min(),
                'avg_nav': performance_data['Latest_NAV'].mean()
            }
        
        # KPIs de Riesgo
        if risk_data:
            sharpe_ratios = [d['sharpe_ratio'] for d in risk_data.values()]
            drawdowns = [d['max_drawdown'] for d in risk_data.values()]
            volatilities = [d['nav_volatility_annualized'] for d in risk_data.values()]
            
            kpis['risk'] = {
                'avg_sharpe_ratio': np.mean(sharpe_ratios),
                'best_sharpe_ratio': max(sharpe_ratios),
                'worst_max_drawdown': min(drawdowns),
                'avg_volatility': np.mean(volatilities),
                'funds_with_good_sharpe': sum(1 for s in sharpe_ratios if s > 0.5)
            }
        
        # KPIs de Diversificación
        if positions_data:
            position_counts = [d['position_count'] for d in positions_data.values()]
            total_positions = sum(position_counts)
            
            kpis['diversification'] = {
                'total_positions': total_positions,
                'avg_positions_per_fund': np.mean(position_counts),
                'max_positions_in_fund': max(position_counts),
                'well_diversified_funds': sum(1 for p in position_counts if p >= 10)
            }
        
        # Mostrar KPIs
        for category, metrics in kpis.items():
            print(f"\n📈 {category.upper()} KPIs:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    if 'return' in key or 'ratio' in key:
                        print(f"  • {key.replace('_', ' ').title()}: {value:.2%}")
                    else:
                        print(f"  • {key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"  • {key.replace('_', ' ').title()}: {value:,}")
        
        return kpis
        
    except Exception as e:
        print(f"❌ Error generando KPIs: {e}")
        return {}

def main():
    print("🚀 INVESTMENT DATA ANALYSIS AGENT - SISTEMA DE ANÁLISIS IA ACTIVADO")
    print("🎯 Analizando fondos activos en GD_Fondos donde FN_Activo = 1")
    print("=" * 90)
    
    try:
        engine = get_sql_server_engine()
        print(f"✅ Conectado a: {settings.SOURCE_DB_HOST}/{settings.SOURCE_DB_NAME}")
        
        # 1. Obtener fondos activos
        active_funds = get_active_funds(engine)
        
        if active_funds.empty:
            print("❌ No se encontraron fondos activos")
            return
        
        fund_ids = active_funds['PshipID'].tolist()
        
        # 2. Análisis de performance
        performance_data = analyze_portfolio_performance(engine, fund_ids)
        
        # 3. Análisis de posiciones
        positions_data = analyze_positions_composition(engine, fund_ids)
        
        # 4. Análisis de riesgo
        risk_data = calculate_risk_metrics(engine, fund_ids)
        
        # 5. Generar insights con IA
        ai_insights = generate_ai_insights(performance_data, positions_data, risk_data)
        
        # 6. Crear KPIs para dashboard
        dashboard_kpis = create_investment_kpis(performance_data, positions_data, risk_data)
        
        print("\n" + "🎉" * 30)
        print("✅ SISTEMA DE ANÁLISIS IA COMPLETADO EXITOSAMENTE")
        print(f"📊 Fondos Analizados: {len(fund_ids)}")
        print("🚀 Listo para exportar a Power BI, Excel o Data Studio")
        print("🤖 IA ha generado insights automáticos y recomendaciones")
        print("🎉" * 30)
        
    except Exception as e:
        print(f"❌ Error en el sistema de análisis IA: {e}")

if __name__ == "__main__":
    main()