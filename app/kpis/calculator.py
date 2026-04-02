"""
KPI Calculation Service for Investment Data
Calculates key performance indicators and financial metrics for portfolios.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import structlog

from app.database.connection import DatabaseManager
from app.core.config import kpi_settings
from app.core.logging_config import log_analysis_operation

logger = structlog.get_logger(__name__)


class InvestmentKPIService:
    """
    Service for calculating investment KPIs and performance metrics.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize KPI service
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.risk_free_rate = kpi_settings.RISK_FREE_RATE
        
    async def calculate_portfolio_kpis(
        self,
        portfolio_id: int,
        calculation_date: Optional[date] = None,
        period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive KPIs for a portfolio
        
        Args:
            portfolio_id: Portfolio ID
            calculation_date: Date for calculations (default: today)
            period_days: Analysis period in days
            
        Returns:
            Dictionary with calculated KPIs
        """
        try:
            start_time = datetime.utcnow()
            
            if not calculation_date:
                calculation_date = date.today()
            
            start_date = calculation_date - timedelta(days=period_days)
            
            logger.info("Calculating portfolio KPIs",
                       portfolio_id=portfolio_id,
                       calculation_date=calculation_date.isoformat(),
                       period_days=period_days)
            
            # Get portfolio basic info
            portfolio_info = await self._get_portfolio_info(portfolio_id)
            if not portfolio_info:
                raise ValueError(f"Portfolio {portfolio_id} not found")
            
            # Calculate various KPIs
            kpis = {}
            
            # 1. Returns KPIs
            return_metrics = await self._calculate_return_metrics(
                portfolio_id, start_date, calculation_date
            )
            kpis.update(return_metrics)
            
            # 2. Risk KPIs
            risk_metrics = await self._calculate_risk_metrics(
                portfolio_id, start_date, calculation_date
            )
            kpis.update(risk_metrics)
            
            # 3. Valuation KPIs
            valuation_metrics = await self._calculate_valuation_metrics(
                portfolio_id, calculation_date
            )
            kpis.update(valuation_metrics)
            
            # 4. Liquidity KPIs
            liquidity_metrics = await self._calculate_liquidity_metrics(
                portfolio_id, calculation_date
            )
            kpis.update(liquidity_metrics)
            
            # 5. Allocation KPIs
            allocation_metrics = await self._calculate_allocation_metrics(
                portfolio_id, calculation_date
            )
            kpis.update(allocation_metrics)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_analysis_operation(
                logger, "kpi_calculation",
                record_count=len(kpis),
                duration=duration
            )
            
            result = {
                "portfolio_id": portfolio_id,
                "portfolio_code": portfolio_info["portfolio_code"],
                "calculation_date": calculation_date.isoformat(),
                "period_days": period_days,
                "kpis": kpis,
                "calculation_metadata": {
                    "calculated_at": datetime.utcnow().isoformat(),
                    "duration_seconds": duration,
                    "kpi_count": len(kpis)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error("KPI calculation failed", 
                        portfolio_id=portfolio_id, error=str(e))
            raise
    
    async def _get_portfolio_info(self, portfolio_id: int) -> Optional[Dict[str, Any]]:
        """Get basic portfolio information"""
        try:
            query = """
            SELECT portfolio_id, portfolio_code, portfolio_name, 
                   portfolio_type, currency, inception_date, benchmark
            FROM Portfolios 
            WHERE portfolio_id = :portfolio_id
            """
            
            df = await self.db_manager.execute_query(query, {"portfolio_id": portfolio_id})
            
            if df.empty:
                return None
            
            return df.iloc[0].to_dict()
            
        except Exception as e:
            logger.error("Failed to get portfolio info", portfolio_id=portfolio_id, error=str(e))
            return None
    
    async def _calculate_return_metrics(
        self, 
        portfolio_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, float]:
        """
        Calculate return-based KPIs
        
        Returns:
            Dictionary with return metrics
        """
        try:
            # Get portfolio values over time
            query = """
            WITH PortfolioValues AS (
                SELECT 
                    pl.period_end as value_date,
                    pl.ending_value
                FROM ProfitLoss pl
                WHERE pl.portfolio_id = :portfolio_id
                AND pl.period_end BETWEEN :start_date AND :end_date
                AND pl.period_type = 'daily'
                ORDER BY pl.period_end
            )
            SELECT value_date, ending_value
            FROM PortfolioValues
            """
            
            params = {
                "portfolio_id": portfolio_id,
                "start_date": start_date,
                "end_date": end_date
            }
            
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty or len(df) < 2:
                return {
                    "total_return": 0.0,
                    "annualized_return": 0.0,
                    "cumulative_return": 0.0
                }
            
            # Calculate returns
            values = df["ending_value"].values
            daily_returns = np.diff(values) / values[:-1]
            
            # Total return
            total_return = (values[-1] - values[0]) / values[0]
            
            # Annualized return
            days = len(df) - 1
            annualized_return = (1 + total_return) ** (365.0 / days) - 1
            
            # Cumulative return
            cumulative_return = (1 + daily_returns).prod() - 1
            
            return {
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "cumulative_return": float(cumulative_return)
            }
            
        except Exception as e:
            logger.warning("Failed to calculate return metrics", error=str(e))
            return {"total_return": 0.0, "annualized_return": 0.0, "cumulative_return": 0.0}
    
    async def _calculate_risk_metrics(
        self, 
        portfolio_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, float]:
        """
        Calculate risk-based KPIs
        
        Returns:
            Dictionary with risk metrics
        """
        try:
            # Get daily returns
            query = """
            WITH DailyReturns AS (
                SELECT 
                    pl.period_end,
                    pl.ending_value,
                    LAG(pl.ending_value) OVER (ORDER BY pl.period_end) as prev_value
                FROM ProfitLoss pl
                WHERE pl.portfolio_id = :portfolio_id
                AND pl.period_end BETWEEN :start_date AND :end_date
                AND pl.period_type = 'daily'
                ORDER BY pl.period_end
            )
            SELECT 
                period_end,
                CASE 
                    WHEN prev_value IS NOT NULL AND prev_value > 0
                    THEN (ending_value - prev_value) / prev_value
                    ELSE NULL
                END as daily_return
            FROM DailyReturns
            WHERE prev_value IS NOT NULL
            """
            
            params = {
                "portfolio_id": portfolio_id,
                "start_date": start_date,
                "end_date": end_date
            }
            
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty:
                return {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "var_95": 0.0,
                    "var_99": 0.0
                }
            
            returns = df["daily_return"].dropna().values
            
            if len(returns) < 10:
                return {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "var_95": 0.0,
                    "var_99": 0.0
                }
            
            # Volatility (annualized)
            volatility = np.std(returns) * np.sqrt(252)
            
            # Sharpe Ratio
            excess_return = np.mean(returns) * 252 - self.risk_free_rate
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0
            
            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Value at Risk
            var_95 = np.percentile(returns, 5)  # 5th percentile
            var_99 = np.percentile(returns, 1)  # 1st percentile
            
            return {
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(abs(max_drawdown)),
                "var_95": float(abs(var_95)),
                "var_99": float(abs(var_99))
            }
            
        except Exception as e:
            logger.warning("Failed to calculate risk metrics", error=str(e))
            return {
                "volatility": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "var_95": 0.0,
                "var_99": 0.0
            }
    
    async def _calculate_valuation_metrics(
        self, 
        portfolio_id: int, 
        calculation_date: date
    ) -> Dict[str, float]:
        """
        Calculate valuation KPIs
        
        Returns:
            Dictionary with valuation metrics
        """
        try:
            query = """
            WITH CurrentPositions AS (
                SELECT 
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'buy' THEN t.net_amount
                            WHEN t.transaction_type = 'sell' THEN -t.net_amount
                            ELSE 0
                        END
                    ) as book_value,
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'buy' THEN t.quantity
                            WHEN t.transaction_type = 'sell' THEN -t.quantity
                            ELSE 0
                        END * md.close_price
                    ) as market_value
                FROM Transactions t
                INNER JOIN MarketData md ON t.asset_id = md.asset_id
                WHERE t.portfolio_id = :portfolio_id
                AND t.transaction_date <= :calculation_date
                AND md.price_date = (
                    SELECT MAX(price_date)
                    FROM MarketData md2
                    WHERE md2.asset_id = md.asset_id
                    AND md2.price_date <= :calculation_date
                )
            )
            SELECT book_value, market_value
            FROM CurrentPositions
            """
            
            params = {
                "portfolio_id": portfolio_id,
                "calculation_date": calculation_date
            }
            
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty:
                return {"current_value": 0.0, "unrealized_pnl": 0.0, "unrealized_pnl_percent": 0.0}
            
            row = df.iloc[0]
            book_value = row["book_value"] or 0
            market_value = row["market_value"] or 0
            
            unrealized_pnl = market_value - book_value
            unrealized_pnl_percent = (unrealized_pnl / book_value * 100) if book_value > 0 else 0
            
            return {
                "current_value": float(market_value),
                "unrealized_pnl": float(unrealized_pnl),
                "unrealized_pnl_percent": float(unrealized_pnl_percent)
            }
            
        except Exception as e:
            logger.warning("Failed to calculate valuation metrics", error=str(e))
            return {"current_value": 0.0, "unrealized_pnl": 0.0, "unrealized_pnl_percent": 0.0}
    
    async def _calculate_liquidity_metrics(
        self, 
        portfolio_id: int, 
        calculation_date: date
    ) -> Dict[str, float]:
        """
        Calculate liquidity KPIs
        
        Returns:
            Dictionary with liquidity metrics
        """
        try:
            # Simple liquidity score based on asset types and volumes
            query = """
            SELECT 
                a.asset_type,
                COUNT(*) as position_count,
                SUM(md.volume) as total_volume
            FROM Transactions t
            INNER JOIN Assets a ON t.asset_id = a.asset_id
            INNER JOIN MarketData md ON a.asset_id = md.asset_id
            WHERE t.portfolio_id = :portfolio_id
            AND t.transaction_date <= :calculation_date
            AND md.price_date = (
                SELECT MAX(price_date)
                FROM MarketData md2
                WHERE md2.asset_id = md.asset_id
                AND md2.price_date <= :calculation_date
            )
            GROUP BY a.asset_type
            """
            
            params = {
                "portfolio_id": portfolio_id,
                "calculation_date": calculation_date
            }
            
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty:
                return {"liquidity_score": 0.0, "liquid_positions_percent": 0.0}
            
            # Simple liquidity scoring
            liquidity_weights = {
                "stock": 0.8,
                "etf": 0.9,
                "bond": 0.6,
                "cash": 1.0,
                "mutual_fund": 0.7
            }
            
            total_positions = df["position_count"].sum()
            weighted_liquidity = 0
            
            for _, row in df.iterrows():
                asset_type = row["asset_type"]
                position_count = row["position_count"]
                weight = liquidity_weights.get(asset_type, 0.5)
                weighted_liquidity += weight * position_count
            
            liquidity_score = weighted_liquidity / total_positions if total_positions > 0 else 0
            
            # Calculate liquid positions percentage
            liquid_types = ["stock", "etf", "cash"]
            liquid_positions = df[df["asset_type"].isin(liquid_types)]["position_count"].sum()
            liquid_percent = (liquid_positions / total_positions * 100) if total_positions > 0 else 0
            
            return {
                "liquidity_score": float(liquidity_score),
                "liquid_positions_percent": float(liquid_percent)
            }
            
        except Exception as e:
            logger.warning("Failed to calculate liquidity metrics", error=str(e))
            return {"liquidity_score": 0.0, "liquid_positions_percent": 0.0}
    
    async def _calculate_allocation_metrics(
        self, 
        portfolio_id: int, 
        calculation_date: date
    ) -> Dict[str, Any]:
        """
        Calculate allocation KPIs
        
        Returns:
            Dictionary with allocation metrics
        """
        try:
            query = """
            WITH CurrentPositions AS (
                SELECT 
                    a.asset_type,
                    a.sector,
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'buy' THEN t.quantity
                            WHEN t.transaction_type = 'sell' THEN -t.quantity
                            ELSE 0
                        END * md.close_price
                    ) as position_value
                FROM Transactions t
                INNER JOIN Assets a ON t.asset_id = a.asset_id
                INNER JOIN MarketData md ON a.asset_id = md.asset_id
                WHERE t.portfolio_id = :portfolio_id
                AND t.transaction_date <= :calculation_date
                AND md.price_date = (
                    SELECT MAX(price_date)
                    FROM MarketData md2
                    WHERE md2.asset_id = md.asset_id
                    AND md2.price_date <= :calculation_date
                )
                GROUP BY a.asset_type, a.sector
                HAVING SUM(
                    CASE 
                        WHEN t.transaction_type = 'buy' THEN t.quantity
                        WHEN t.transaction_type = 'sell' THEN -t.quantity
                        ELSE 0
                    END
                ) > 0
            )
            SELECT 
                asset_type,
                sector,
                position_value,
                SUM(position_value) OVER() as total_value
            FROM CurrentPositions
            ORDER BY position_value DESC
            """
            
            params = {
                "portfolio_id": portfolio_id,
                "calculation_date": calculation_date
            }
            
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty:
                return {
                    "asset_allocation": {},
                    "sector_allocation": {},
                    "concentration_risk": 0.0,
                    "diversification_score": 0.0
                }
            
            total_value = df["total_value"].iloc[0]
            
            # Asset type allocation
            asset_allocation = {}
            asset_groups = df.groupby("asset_type")["position_value"].sum()
            for asset_type, value in asset_groups.items():
                asset_allocation[asset_type] = float(value / total_value * 100)
            
            # Sector allocation
            sector_allocation = {}
            sector_groups = df.groupby("sector")["position_value"].sum()
            for sector, value in sector_groups.items():
                if pd.notna(sector):
                    sector_allocation[sector] = float(value / total_value * 100)
            
            # Concentration risk (largest single position %)
            max_position = df["position_value"].max()
            concentration_risk = float(max_position / total_value * 100)
            
            # Diversification score (based on number of positions and allocation evenness)
            position_count = len(df)
            allocation_variance = np.var([v / total_value for v in df["position_value"]])
            diversification_score = min(100, (position_count / 20) * 50 + (1 - allocation_variance) * 50)
            
            return {
                "asset_allocation": asset_allocation,
                "sector_allocation": sector_allocation,
                "concentration_risk": float(concentration_risk),
                "diversification_score": float(diversification_score)
            }
            
        except Exception as e:
            logger.warning("Failed to calculate allocation metrics", error=str(e))
            return {
                "asset_allocation": {},
                "sector_allocation": {},
                "concentration_risk": 0.0,
                "diversification_score": 0.0
            }