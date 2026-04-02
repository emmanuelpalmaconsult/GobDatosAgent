"""
Main Service Layer for Investment Data Analysis Agent
Orchestrates business logic and coordinates between different modules.
"""

from typing import List, Dict, Any, Optional
from datetime import date
import structlog
import pandas as pd
import numpy as np

from app.database.connection import DatabaseManager
from app.analysis.ai_service import InvestmentAnalysisService
from app.kpis.calculator import InvestmentKPIService
from app.exports.bi_service import BIExportService

logger = structlog.get_logger(__name__)


class InvestmentDataService:
    """
    Main orchestration service for investment data operations.
    Coordinates between analysis, KPI calculation, and export services.
    """
    
    def __init__(self):
        """Initialize the investment data service"""
        self.db_manager = None
        self.analysis_service = None
        self.kpi_service = None
        self.export_service = None
        
    async def initialize(self):
        """Initialize database connection and services"""
        try:
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.connect()
            
            # Initialize specialized services
            self.analysis_service = InvestmentAnalysisService(self.db_manager)
            self.kpi_service = InvestmentKPIService(self.db_manager)
            self.export_service = BIExportService(self.db_manager)
            
            logger.info("Investment data service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize investment data service", error=str(e))
            raise
    
    async def shutdown(self):
        """Shutdown service and cleanup connections"""
        try:
            if self.db_manager:
                await self.db_manager.disconnect()
            logger.info("Investment data service shutdown completed")
        except Exception as e:
            logger.error("Error during service shutdown", error=str(e))
    
    async def get_portfolio_comprehensive_analysis(
        self,
        portfolio_id: int,
        analysis_date: Optional[date] = None,
        period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Get comprehensive analysis for a portfolio including KPIs, insights, and correlations
        
        Args:
            portfolio_id: Portfolio ID to analyze
            analysis_date: Date for analysis (default: today)
            period_days: Analysis period in days
            
        Returns:
            Comprehensive portfolio analysis
        """
        try:
            logger.info("Starting comprehensive portfolio analysis", 
                       portfolio_id=portfolio_id)
            
            if not analysis_date:
                analysis_date = date.today()
            
            # Run parallel analysis
            results = {}
            
            # 1. Calculate KPIs
            try:
                kpis = await self.kpi_service.calculate_portfolio_kpis(
                    portfolio_id, analysis_date, period_days
                )
                results["kpis"] = kpis
            except Exception as e:
                logger.warning("KPI calculation failed", error=str(e))
                results["kpis"] = {"error": str(e)}
            
            # 2. Correlation analysis (with other portfolios if applicable)
            try:
                correlations = await self.analysis_service.analyze_portfolio_correlations(
                    [portfolio_id], 
                    analysis_date - pd.Timedelta(days=period_days),
                    analysis_date
                )
                results["correlations"] = correlations
            except Exception as e:
                logger.warning("Correlation analysis failed", error=str(e))
                results["correlations"] = {"error": str(e)}
            
            # 3. Portfolio positions and allocation
            try:
                positions = await self._get_portfolio_positions_summary(portfolio_id, analysis_date)
                results["positions"] = positions
            except Exception as e:
                logger.warning("Position analysis failed", error=str(e))
                results["positions"] = {"error": str(e)}
            
            # 4. Generate executive summary
            summary = self._generate_executive_summary(results)
            results["executive_summary"] = summary
            
            logger.info("Comprehensive portfolio analysis completed", 
                       portfolio_id=portfolio_id)
            
            return {
                "portfolio_id": portfolio_id,
                "analysis_date": analysis_date.isoformat(),
                "analysis_period_days": period_days,
                "results": results,
                "generated_at": pd.Timestamp.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Comprehensive portfolio analysis failed", 
                        portfolio_id=portfolio_id, error=str(e))
            raise
    
    async def generate_multi_portfolio_insights(
        self,
        portfolio_ids: List[int],
        analysis_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate insights across multiple portfolios
        
        Args:
            portfolio_ids: List of portfolio IDs
            analysis_date: Analysis date
            
        Returns:
            Multi-portfolio insights and comparisons
        """
        try:
            logger.info("Generating multi-portfolio insights", 
                       portfolio_count=len(portfolio_ids))
            
            if not analysis_date:
                analysis_date = date.today()
            
            insights = {}
            
            # Cross-portfolio correlation analysis
            correlations = await self.analysis_service.analyze_portfolio_correlations(
                portfolio_ids, 
                analysis_date - pd.Timedelta(days=365),
                analysis_date
            )
            insights["cross_correlations"] = correlations
            
            # Performance comparison
            performance_comparison = []
            for portfolio_id in portfolio_ids:
                try:
                    kpis = await self.kpi_service.calculate_portfolio_kpis(
                        portfolio_id, analysis_date
                    )
                    performance_comparison.append(kpis)
                except Exception as e:
                    logger.warning("Performance calculation failed for portfolio", 
                                  portfolio_id=portfolio_id, error=str(e))
            
            insights["performance_comparison"] = performance_comparison
            
            # Generate recommendations
            recommendations = self._generate_portfolio_recommendations(
                correlations, performance_comparison
            )
            insights["recommendations"] = recommendations
            
            return {
                "portfolio_ids": portfolio_ids,
                "analysis_date": analysis_date.isoformat(),
                "insights": insights,
                "generated_at": pd.Timestamp.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Multi-portfolio insights generation failed", error=str(e))
            raise
    
    async def _get_portfolio_positions_summary(
        self, 
        portfolio_id: int, 
        as_of_date: date
    ) -> Dict[str, Any]:
        """Get portfolio positions summary"""
        try:
            query = """
            WITH CurrentPositions AS (
                SELECT 
                    t.asset_id,
                    a.asset_code,
                    a.asset_name,
                    a.asset_type,
                    a.sector,
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'buy' THEN t.quantity
                            WHEN t.transaction_type = 'sell' THEN -t.quantity
                            ELSE 0
                        END
                    ) as current_quantity,
                    AVG(t.price) as avg_cost
                FROM Transactions t
                INNER JOIN Assets a ON t.asset_id = a.asset_id
                WHERE t.portfolio_id = :portfolio_id
                AND t.transaction_date <= :as_of_date
                GROUP BY t.asset_id, a.asset_code, a.asset_name, a.asset_type, a.sector
                HAVING SUM(
                    CASE 
                        WHEN t.transaction_type = 'buy' THEN t.quantity
                        WHEN t.transaction_type = 'sell' THEN -t.quantity
                        ELSE 0
                    END
                ) > 0
            )
            SELECT * FROM CurrentPositions
            ORDER BY (current_quantity * avg_cost) DESC
            """
            
            df = await self.db_manager.execute_query(
                query, {"portfolio_id": portfolio_id, "as_of_date": as_of_date}
            )
            
            if df.empty:
                return {"positions": [], "summary": {}}
            
            # Calculate summary statistics
            total_positions = len(df)
            asset_types = df['asset_type'].value_counts().to_dict()
            sectors = df['sector'].value_counts().to_dict() if 'sector' in df.columns else {}
            
            return {
                "positions": df.to_dict('records'),
                "summary": {
                    "total_positions": total_positions,
                    "asset_type_breakdown": asset_types,
                    "sector_breakdown": sectors
                }
            }
            
        except Exception as e:
            logger.error("Failed to get portfolio positions", error=str(e))
            raise
    
    def _generate_executive_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from analysis results"""
        summary = {
            "status": "completed",
            "key_findings": [],
            "recommendations": [],
            "risk_alerts": []
        }
        
        # Analyze KPIs for key findings
        kpis = analysis_results.get("kpis", {})
        if "kpis" in kpis and isinstance(kpis["kpis"], dict):
            kpi_data = kpis["kpis"]
            
            # Performance findings
            if "annualized_return" in kpi_data:
                returns = kpi_data["annualized_return"]
                if returns > 0.15:
                    summary["key_findings"].append("Strong performance with annualized return > 15%")
                elif returns < 0:
                    summary["key_findings"].append("Negative returns require attention")
            
            # Risk findings
            if "sharpe_ratio" in kpi_data:
                sharpe = kpi_data["sharpe_ratio"]
                if sharpe > 1.0:
                    summary["key_findings"].append("Excellent risk-adjusted returns (Sharpe > 1.0)")
                elif sharpe < 0:
                    summary["risk_alerts"].append("Poor risk-adjusted performance")
            
            # Volatility alerts
            if "volatility" in kpi_data:
                vol = kpi_data["volatility"]
                if vol > 0.25:
                    summary["risk_alerts"].append("High volatility detected (>25%)")
        
        # Correlation insights
        correlations = analysis_results.get("correlations", {})
        if correlations.get("status") == "success":
            insights = correlations.get("insights", [])
            for insight in insights:
                if insight.get("importance") == "high":
                    summary["risk_alerts"].append(insight["title"])
                else:
                    summary["recommendations"].append(insight.get("recommendation", ""))
        
        return summary
    
    def _generate_portfolio_recommendations(
        self, 
        correlations: Dict[str, Any], 
        performance_data: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate portfolio recommendations based on analysis"""
        recommendations = []
        
        # Performance-based recommendations
        if performance_data:
            avg_return = np.mean([p.get("kpis", {}).get("annualized_return", 0) for p in performance_data])
            if avg_return < 0.05:  # Less than 5% return
                recommendations.append({
                    "type": "performance",
                    "recommendation": "Consider reviewing investment strategy as average returns are below 5%"
                })
        
        # Correlation-based recommendations
        if correlations.get("status") == "success":
            avg_correlation = correlations.get("statistics", {}).get("average_correlation", 0)
            if avg_correlation > 0.7:
                recommendations.append({
                    "type": "diversification",
                    "recommendation": "High correlation detected - consider diversifying across asset classes"
                })
        
        return recommendations