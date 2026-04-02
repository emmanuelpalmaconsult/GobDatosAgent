"""
Export Service for Business Intelligence Tools
Handles data export to Power BI, Data Studio, Excel, and Python charts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import json
import os
from pathlib import Path
import structlog

from app.database.connection import DatabaseManager
from app.core.config import settings
from app.core.logging_config import log_export_operation

logger = structlog.get_logger(__name__)


class BIExportService:
    """
    Service for exporting investment data to various BI tools and formats.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize export service
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.export_path = Path(settings.EXPORT_PATH)
        self.export_path.mkdir(exist_ok=True)
        
    async def export_to_powerbi(
        self,
        portfolio_ids: List[int],
        data_types: List[str],
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export portfolio data for Power BI consumption
        
        Args:
            portfolio_ids: List of portfolio IDs to export
            data_types: Types of data to export (portfolios, transactions, kpis, etc.)
            export_format: Export format (json, csv, parquet)
            
        Returns:
            Export result with file paths and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info("Starting Power BI export",
                       portfolio_count=len(portfolio_ids),
                       data_types=data_types)
            
            export_data = {}
            file_paths = []
            record_count = 0
            
            # Export each requested data type
            for data_type in data_types:
                if data_type == "portfolios":
                    data, records = await self._export_portfolios_data(portfolio_ids)
                    export_data["portfolios"] = data
                    record_count += records
                    
                elif data_type == "transactions":
                    data, records = await self._export_transactions_data(portfolio_ids)
                    export_data["transactions"] = data
                    record_count += records
                    
                elif data_type == "kpis":
                    data, records = await self._export_kpis_data(portfolio_ids)
                    export_data["kpis"] = data
                    record_count += records
                    
                elif data_type == "positions":
                    data, records = await self._export_positions_data(portfolio_ids)
                    export_data["positions"] = data
                    record_count += records
            
            # Save export files
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "json":
                file_path = self.export_path / f"powerbi_export_{timestamp}.json"
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                file_paths.append(str(file_path))
                
            elif export_format == "csv":
                # Export each data type as separate CSV
                for data_type, data_df in export_data.items():
                    if isinstance(data_df, pd.DataFrame) and not data_df.empty:
                        file_path = self.export_path / f"powerbi_{data_type}_{timestamp}.csv"
                        data_df.to_csv(file_path, index=False)
                        file_paths.append(str(file_path))
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_export_operation(
                logger, "powerbi", "power_bi_cloud", 
                file_path=str(file_paths[0]) if file_paths else None,
                record_count=record_count
            )
            
            return {
                "status": "success",
                "export_type": "powerbi",
                "export_format": export_format,
                "file_paths": file_paths,
                "record_count": record_count,
                "data_types": data_types,
                "portfolios": portfolio_ids,
                "exported_at": datetime.utcnow().isoformat(),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error("Power BI export failed", error=str(e))
            raise
    
    async def export_to_excel(
        self,
        portfolio_ids: List[int],
        data_types: List[str],
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Export portfolio data to Excel with multiple sheets and charts
        
        Args:
            portfolio_ids: List of portfolio IDs to export
            data_types: Types of data to export
            include_charts: Whether to include charts in Excel
            
        Returns:
            Export result with file path and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info("Starting Excel export",
                       portfolio_count=len(portfolio_ids),
                       include_charts=include_charts)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_path = self.export_path / f"investment_report_{timestamp}.xlsx"
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                record_count = 0
                
                # Export portfolios summary
                if "portfolios" in data_types:
                    portfolios_df, records = await self._export_portfolios_data(portfolio_ids)
                    portfolios_df.to_excel(writer, sheet_name='Portfolios', index=False)
                    record_count += records
                
                # Export transactions
                if "transactions" in data_types:
                    transactions_df, records = await self._export_transactions_data(portfolio_ids)
                    transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
                    record_count += records
                
                # Export KPIs
                if "kpis" in data_types:
                    kpis_df, records = await self._export_kpis_data(portfolio_ids)
                    kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
                    record_count += records
                
                # Export positions
                if "positions" in data_types:
                    positions_df, records = await self._export_positions_data(portfolio_ids)
                    positions_df.to_excel(writer, sheet_name='Positions', index=False)
                    record_count += records
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_export_operation(
                logger, "excel", "local_file",
                file_path=str(file_path),
                record_count=record_count
            )
            
            return {
                "status": "success",
                "export_type": "excel",
                "file_path": str(file_path),
                "record_count": record_count,
                "data_types": data_types,
                "portfolios": portfolio_ids,
                "exported_at": datetime.utcnow().isoformat(),
                "duration_seconds": duration,
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            logger.error("Excel export failed", error=str(e))
            raise
    
    async def _export_portfolios_data(self, portfolio_ids: List[int]) -> tuple[pd.DataFrame, int]:
        """Export portfolios basic data"""
        try:
            query = """
            SELECT 
                p.portfolio_id,
                p.portfolio_code,
                p.portfolio_name,
                p.portfolio_type,
                p.currency,
                p.inception_date,
                p.manager_name,
                p.benchmark,
                p.risk_profile,
                p.status,
                COALESCE(pv.current_value, 0) as current_value,
                COALESCE(pv.total_return, 0) as total_return
            FROM Portfolios p
            LEFT JOIN (
                SELECT 
                    portfolio_id,
                    SUM(net_amount) as current_value,
                    0 as total_return
                FROM Transactions 
                WHERE portfolio_id IN ({portfolio_ids_placeholder})
                GROUP BY portfolio_id  
            ) pv ON p.portfolio_id = pv.portfolio_id
            WHERE p.portfolio_id IN ({portfolio_ids_placeholder})
            """
            
            # Create placeholders
            placeholders = ",".join(f":portfolio_{i}" for i in range(len(portfolio_ids)))
            query = query.replace("{portfolio_ids_placeholder}", placeholders)
            
            # Build parameters
            params = {}
            for i, portfolio_id in enumerate(portfolio_ids):
                params[f"portfolio_{i}"] = portfolio_id
            
            df = await self.db_manager.execute_query(query, params)
            return df, len(df)
            
        except Exception as e:
            logger.warning("Failed to export portfolios data", error=str(e))
            return pd.DataFrame(), 0
    
    async def _export_transactions_data(self, portfolio_ids: List[int]) -> tuple[pd.DataFrame, int]:
        """Export transactions data"""
        try:
            query = """
            SELECT 
                t.transaction_id,
                t.portfolio_id,
                p.portfolio_code,
                t.asset_id,
                a.asset_code,
                a.asset_name,
                t.transaction_type,
                t.transaction_date,
                t.quantity,
                t.price,
                t.gross_amount,
                t.net_amount,
                t.fees,
                t.taxes,
                t.transaction_currency
            FROM Transactions t
            INNER JOIN Portfolios p ON t.portfolio_id = p.portfolio_id
            INNER JOIN Assets a ON t.asset_id = a.asset_id
            WHERE t.portfolio_id IN ({portfolio_ids_placeholder})
            ORDER BY t.transaction_date DESC
            """
            
            # Create placeholders
            placeholders = ",".join(f":portfolio_{i}" for i in range(len(portfolio_ids)))
            query = query.replace("{portfolio_ids_placeholder}", placeholders)
            
            # Build parameters
            params = {}
            for i, portfolio_id in enumerate(portfolio_ids):
                params[f"portfolio_{i}"] = portfolio_id
            
            df = await self.db_manager.execute_query(query, params)
            return df, len(df)
            
        except Exception as e:
            logger.warning("Failed to export transactions data", error=str(e))
            return pd.DataFrame(), 0
    
    async def _export_kpis_data(self, portfolio_ids: List[int]) -> tuple[pd.DataFrame, int]:
        """Export KPIs data"""
        try:
            # This is a simplified version - in practice, you'd calculate current KPIs
            query = """
            SELECT 
                p.portfolio_id,
                p.portfolio_code,
                p.portfolio_name,
                COALESCE(perf.total_return, 0) as total_return,
                COALESCE(perf.volatility, 0) as volatility,
                COALESCE(perf.sharpe_ratio, 0) as sharpe_ratio,
                COALESCE(perf.max_drawdown, 0) as max_drawdown,
                perf.calculation_date
            FROM Portfolios p
            LEFT JOIN (
                SELECT 
                    portfolio_id,
                    total_return,
                    volatility,
                    sharpe_ratio,
                    max_drawdown,
                    calculation_date,
                    ROW_NUMBER() OVER (PARTITION BY portfolio_id ORDER BY calculation_date DESC) as rn
                FROM Performance
            ) perf ON p.portfolio_id = perf.portfolio_id AND perf.rn = 1
            WHERE p.portfolio_id IN ({portfolio_ids_placeholder})
            """
            
            # Create placeholders
            placeholders = ",".join(f":portfolio_{i}" for i in range(len(portfolio_ids)))
            query = query.replace("{portfolio_ids_placeholder}", placeholders)
            
            # Build parameters
            params = {}
            for i, portfolio_id in enumerate(portfolio_ids):
                params[f"portfolio_{i}"] = portfolio_id
            
            df = await self.db_manager.execute_query(query, params)
            return df, len(df)
            
        except Exception as e:
            logger.warning("Failed to export KPIs data", error=str(e))
            return pd.DataFrame(), 0
    
    async def _export_positions_data(self, portfolio_ids: List[int]) -> tuple[pd.DataFrame, int]:
        """Export current positions data"""
        try:
            query = """
            WITH CurrentPositions AS (
                SELECT 
                    t.portfolio_id,
                    t.asset_id,
                    SUM(
                        CASE 
                            WHEN t.transaction_type = 'buy' THEN t.quantity
                            WHEN t.transaction_type = 'sell' THEN -t.quantity
                            ELSE 0
                        END
                    ) as current_quantity,
                    AVG(
                        CASE 
                            WHEN t.transaction_type IN ('buy', 'sell') THEN t.price
                            ELSE NULL
                        END
                    ) as avg_cost
                FROM Transactions t
                WHERE t.portfolio_id IN ({portfolio_ids_placeholder})
                GROUP BY t.portfolio_id, t.asset_id
                HAVING SUM(
                    CASE 
                        WHEN t.transaction_type = 'buy' THEN t.quantity
                        WHEN t.transaction_type = 'sell' THEN -t.quantity
                        ELSE 0
                    END
                ) > 0
            )
            SELECT 
                cp.portfolio_id,
                p.portfolio_code,
                cp.asset_id,
                a.asset_code,
                a.asset_name,
                a.asset_type,
                cp.current_quantity,
                cp.avg_cost,
                COALESCE(md.close_price, 0) as current_price,
                (cp.current_quantity * COALESCE(md.close_price, 0)) as market_value,
                (cp.current_quantity * cp.avg_cost) as book_value
            FROM CurrentPositions cp
            INNER JOIN Portfolios p ON cp.portfolio_id = p.portfolio_id
            INNER JOIN Assets a ON cp.asset_id = a.asset_id
            LEFT JOIN (
                SELECT 
                    asset_id, 
                    close_price,
                    ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY price_date DESC) as rn
                FROM MarketData
            ) md ON cp.asset_id = md.asset_id AND md.rn = 1
            ORDER BY cp.portfolio_id, (cp.current_quantity * COALESCE(md.close_price, 0)) DESC
            """
            
            # Create placeholders
            placeholders = ",".join(f":portfolio_{i}" for i in range(len(portfolio_ids)))
            query = query.replace("{portfolio_ids_placeholder}", placeholders)
            
            # Build parameters
            params = {}
            for i, portfolio_id in enumerate(portfolio_ids):
                params[f"portfolio_{i}"] = portfolio_id
            
            df = await self.db_manager.execute_query(query, params)
            return df, len(df)
            
        except Exception as e:
            logger.warning("Failed to export positions data", error=str(e))
            return pd.DataFrame(), 0