"""
AI Analysis Service for Investment Data
Provides intelligent analysis, correlation detection, and insights generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import structlog
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import warnings

from app.database.connection import DatabaseManager
from app.core.config import settings, kpi_settings
from app.core.logging_config import log_analysis_operation

warnings.filterwarnings('ignore')
logger = structlog.get_logger(__name__)


class InvestmentAnalysisService:
    """
    Core service for AI-powered investment analysis and insights generation.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the analysis service
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.scaler = StandardScaler()
        
    async def analyze_portfolio_correlations(
        self,
        portfolio_ids: List[int],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_periods: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze correlations between assets in portfolios
        
        Args:
            portfolio_ids: List of portfolio IDs to analyze
            start_date: Analysis start date
            end_date: Analysis end date
            min_periods: Minimum periods required for correlation
            
        Returns:
            Correlation analysis results
        """
        try:
            start_time = datetime.utcnow()
            
            # Set default date range if not provided
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=365)  # 1 year default
            
            logger.info("Starting correlation analysis",
                       portfolio_count=len(portfolio_ids),
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat())
            
            # Get portfolio positions and returns data
            returns_data = await self._get_portfolio_returns_data(
                portfolio_ids, start_date, end_date
            )
            
            if returns_data.empty:
                return {
                    "status": "no_data",
                    "message": "Insufficient data for correlation analysis",
                    "portfolios": portfolio_ids,
                    "date_range": {"start": start_date, "end": end_date}
                }
            
            # Calculate correlation matrix
            correlation_matrix = returns_data.corr()
            
            # Find significant correlations
            significant_correlations = self._find_significant_correlations(
                correlation_matrix, threshold=0.7
            )
            
            # Perform clustering analysis
            clusters = await self._perform_asset_clustering(returns_data)
            
            # Generate insights
            insights = self._generate_correlation_insights(
                correlation_matrix, significant_correlations, clusters
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_analysis_operation(
                logger, "correlation_analysis",
                record_count=len(returns_data),
                duration=duration
            )
            
            results = {
                "status": "success",
                "analysis_date": datetime.utcnow().isoformat(),
                "portfolios_analyzed": portfolio_ids,
                "date_range": {"start": start_date, "end": end_date},
                "correlation_matrix": correlation_matrix.to_dict(),
                "significant_correlations": significant_correlations,
                "asset_clusters": clusters,
                "insights": insights,
                "statistics": {
                    "assets_analyzed": len(correlation_matrix.columns),
                    "observations": len(returns_data),
                    "average_correlation": float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()),
                    "analysis_duration_seconds": duration
                }
            }
            
            return results
            
        except Exception as e:
            logger.error("Correlation analysis failed", error=str(e))
            raise
    
    async def _get_portfolio_returns_data(
        self,
        portfolio_ids: List[int],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Get returns data for portfolio assets
        
        Args:
            portfolio_ids: Portfolio IDs
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with returns data
        """
        try:
            # Query to get portfolio holdings and price data
            query = """
            WITH PortfolioHoldings AS (
                SELECT DISTINCT
                    t.portfolio_id,
                    t.asset_id,
                    a.asset_code,
                    a.asset_name
                FROM Transactions t
                INNER JOIN Assets a ON t.asset_id = a.asset_id
                WHERE t.portfolio_id IN ({portfolio_ids_placeholder})
                AND t.transaction_date <= :end_date
            ),
            PriceData AS (
                SELECT 
                    ph.asset_code,
                    md.price_date,
                    md.close_price,
                    LAG(md.close_price) OVER (
                        PARTITION BY ph.asset_id 
                        ORDER BY md.price_date
                    ) as prev_price
                FROM PortfolioHoldings ph
                INNER JOIN MarketData md ON ph.asset_id = md.asset_id
                WHERE md.price_date BETWEEN :start_date AND :end_date
                AND md.close_price IS NOT NULL
            )
            SELECT 
                asset_code,
                price_date,
                CASE 
                    WHEN prev_price IS NOT NULL AND prev_price > 0 
                    THEN (close_price - prev_price) / prev_price
                    ELSE NULL
                END as daily_return
            FROM PriceData
            WHERE prev_price IS NOT NULL
            ORDER BY asset_code, price_date
            """
            
            # Create placeholders for portfolio IDs
            portfolio_placeholders = ",".join(f":portfolio_{i}" for i in range(len(portfolio_ids)))
            query = query.replace("{portfolio_ids_placeholder}", portfolio_placeholders)
            
            # Build parameters
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            for i, portfolio_id in enumerate(portfolio_ids):
                params[f"portfolio_{i}"] = portfolio_id
            
            # Execute query
            df = await self.db_manager.execute_query(query, params)
            
            if df.empty:
                return pd.DataFrame()
            
            # Pivot to get returns matrix
            returns_matrix = df.pivot(
                index='price_date', 
                columns='asset_code', 
                values='daily_return'
            )
            
            # Remove columns with too many NaN values
            returns_matrix = returns_matrix.dropna(thresh=len(returns_matrix) * 0.5, axis=1)
            
            # Forward fill missing values
            returns_matrix = returns_matrix.fillna(method='ffill').fillna(0)
            
            logger.info("Returns data retrieved",
                       assets=len(returns_matrix.columns),
                       observations=len(returns_matrix))
            
            return returns_matrix
            
        except Exception as e:
            logger.error("Failed to get returns data", error=str(e))
            raise
    
    def _find_significant_correlations(
        self, 
        correlation_matrix: pd.DataFrame, 
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find significant correlations in the matrix
        
        Args:
            correlation_matrix: Correlation matrix
            threshold: Correlation threshold for significance
            
        Returns:
            List of significant correlation pairs
        """
        significant_pairs = []
        
        for i, asset1 in enumerate(correlation_matrix.columns):
            for j, asset2 in enumerate(correlation_matrix.columns):
                if i < j:  # Avoid duplicates
                    correlation = correlation_matrix.loc[asset1, asset2]
                    
                    if abs(correlation) >= threshold:
                        significant_pairs.append({
                            "asset1": asset1,
                            "asset2": asset2,
                            "correlation": float(correlation),
                            "relationship": "positive" if correlation > 0 else "negative",
                            "strength": "strong" if abs(correlation) > 0.8 else "moderate"
                        })
        
        # Sort by absolute correlation value
        significant_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        return significant_pairs
    
    async def _perform_asset_clustering(
        self, 
        returns_data: pd.DataFrame, 
        n_clusters: int = None
    ) -> Dict[str, Any]:
        """
        Perform clustering analysis on assets based on returns
        
        Args:
            returns_data: Returns data DataFrame
            n_clusters: Number of clusters (auto-determined if None)
            
        Returns:
            Clustering results
        """
        try:
            if len(returns_data.columns) < 3:
                return {"status": "insufficient_assets", "clusters": {}}
            
            # Prepare data for clustering
            returns_transposed = returns_data.T  # Assets as rows
            
            # Standardize the data
            scaled_data = self.scaler.fit_transform(returns_transposed)
            
            # Determine optimal number of clusters if not provided
            if n_clusters is None:
                n_clusters = min(5, max(2, len(returns_data.columns) // 3))
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            # Organize results
            clusters = {}
            for i, asset in enumerate(returns_data.columns):
                cluster_id = int(cluster_labels[i])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(asset)
            
            # Calculate cluster characteristics
            cluster_stats = {}
            for cluster_id, assets in clusters.items():
                cluster_returns = returns_data[assets]
                cluster_stats[cluster_id] = {
                    "assets": assets,
                    "asset_count": len(assets),
                    "avg_volatility": float(cluster_returns.std().mean()),
                    "avg_return": float(cluster_returns.mean().mean()),
                    "correlation_within_cluster": float(cluster_returns.corr().values[np.triu_indices_from(cluster_returns.corr().values, k=1)].mean())
                }
            
            return {
                "status": "success",
                "n_clusters": n_clusters,
                "clusters": cluster_stats,
                "silhouette_score": self._calculate_silhouette_score(scaled_data, cluster_labels) if len(set(cluster_labels)) > 1 else None
            }
            
        except Exception as e:
            logger.warning("Clustering analysis failed", error=str(e))
            return {"status": "error", "clusters": {}, "error": str(e)}
    
    def _calculate_silhouette_score(self, data: np.ndarray, labels: np.ndarray) -> float:
        """
        Calculate silhouette score for clustering quality
        """
        try:
            from sklearn.metrics import silhouette_score
            return float(silhouette_score(data, labels))
        except:
            return None
    
    def _generate_correlation_insights(
        self,
        correlation_matrix: pd.DataFrame,
        significant_correlations: List[Dict[str, Any]],
        clusters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from correlation analysis
        
        Args:
            correlation_matrix: Correlation matrix
            significant_correlations: Significant correlations
            clusters: Clustering results
            
        Returns:
            List of insights
        """
        insights = []
        
        # High correlation insights
        high_corr_pairs = [pair for pair in significant_correlations if abs(pair["correlation"]) > 0.85]
        if high_corr_pairs:
            insights.append({
                "type": "high_correlation_warning",
                "title": "High Asset Correlations Detected",
                "description": f"Found {len(high_corr_pairs)} asset pairs with correlation > 0.85. This may indicate concentration risk.",
                "importance": "high",
                "recommendation": "Consider diversifying holdings to reduce correlation risk.",
                "details": high_corr_pairs[:3]  # Top 3 pairs
            })
        
        # Diversification insights
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        if avg_correlation > 0.5:
            insights.append({
                "type": "diversification_opportunity",
                "title": "Portfolio Diversification Opportunity",
                "description": f"Average portfolio correlation is {avg_correlation:.2f}, indicating potential for better diversification.",
                "importance": "medium",
                "recommendation": "Consider adding assets from different sectors or asset classes."
            })
        
        # Clustering insights
        if clusters.get("status") == "success" and len(clusters.get("clusters", {})) > 1:
            cluster_count = clusters["n_clusters"]
            insights.append({
                "type": "asset_clustering",
                "title": "Asset Behavior Patterns Identified",
                "description": f"Assets can be grouped into {cluster_count} distinct behavior patterns based on return characteristics.",
                "importance": "medium",
                "recommendation": "Use these patterns for strategic asset allocation and risk management."
            })
        
        # Market regime insights
        recent_volatility = correlation_matrix.std().std()  # Volatility of correlations
        if recent_volatility > 0.3:
            insights.append({
                "type": "market_regime",
                "title": "Volatile Correlation Environment",
                "description": "Asset correlations are showing high variability, suggesting changing market conditions.",
                "importance": "high",
                "recommendation": "Monitor portfolio risk more closely and consider dynamic hedging strategies."
            })
        
        return insights