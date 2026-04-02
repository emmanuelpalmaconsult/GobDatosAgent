"""
Database connection and management for Investment Data Analysis Agent
Handles SQL Server connectivity with connection pooling and health monitoring.
"""

from typing import Optional, Dict, Any, List
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import structlog
import pandas as pd

from app.core.config import settings, db_settings


logger = structlog.get_logger(__name__)


class DatabaseManager:
    """
    Manages database connections for the Investment Data Analysis Agent.
    Supports dual database architecture:
    - Source DB: Extract existing investment data (any DB type)
    - Analytics DB: Store analysis results (PostgreSQL)
    """
    
    def __init__(self):
        """Initialize database manager with dual connection settings"""
        self.source_engine = None      # Source database (investment data)
        self.analytics_engine = None   # Analytics database (PostgreSQL)
        self.SourceSessionLocal = None
        self.AnalyticsSessionLocal = None
        self.metadata = MetaData()
        self._active_tables: Dict[str, bool] = {}
        
    async def connect(self) -> None:
        """Establish database connections for both source and analytics databases"""
        try:
            # Create source database engine (for reading investment data)
            self.source_engine = create_engine(
                settings.source_database_url,
                poolclass=QueuePool,
                pool_size=settings.CONNECTION_POOL_SIZE,
                max_overflow=settings.CONNECTION_POOL_OVERFLOW,
                pool_timeout=settings.CONNECTION_POOL_TIMEOUT,
                echo=settings.DEBUG
            )
            
            # Create analytics database engine (for storing analysis results)
            self.analytics_engine = create_engine(
                settings.analytics_database_url,
                poolclass=QueuePool,
                pool_size=settings.CONNECTION_POOL_SIZE,
                max_overflow=settings.CONNECTION_POOL_OVERFLOW,
                pool_timeout=settings.CONNECTION_POOL_TIMEOUT,
                echo=settings.DEBUG
            )
            
            # Create session makers
            self.SourceSessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.source_engine
            )
            
            self.AnalyticsSessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.analytics_engine
            )
            
            # Test connections
            await self.test_connections()
            
            # Initialize table configurations
            await self._initialize_table_config()
            
            logger.info("Dual database connections established successfully",
                       source_db=settings.SOURCE_DB_TYPE,
                       analytics_db="postgresql")
            
        except Exception as e:
            logger.error("Failed to connect to databases", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Close both database connections"""
        try:
            if self.source_engine:
                self.source_engine.dispose()
            if self.analytics_engine:
                self.analytics_engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.warning("Error during database disconnect", error=str(e))
    
    async def test_connections(self) -> Dict[str, bool]:
        """Test both database connections and return status"""
        status = {"source": False, "analytics": False}
        
        try:
            # Test source database
            with self.source_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                status["source"] = result.fetchone() is not None
        except Exception as e:
            logger.error("Source database connection test failed", error=str(e))
        
        try:
            # Test analytics database
            with self.analytics_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                status["analytics"] = result.fetchone() is not None
        except Exception as e:
            logger.error("Analytics database connection test failed", error=str(e))
        
        return status
    
    def get_source_session(self) -> Session:
        """Get a session for source database (read investment data)"""
        if not self.SourceSessionLocal:
            raise RuntimeError("Source database not connected. Call connect() first.")
        return self.SourceSessionLocal()
    
    def get_analytics_session(self) -> Session:
        """Get a session for analytics database (store analysis results)"""
        if not self.AnalyticsSessionLocal:
            raise RuntimeError("Analytics database not connected. Call connect() first.")
        return self.AnalyticsSessionLocal()
    
    @asynccontextmanager
    async def source_session_scope(self):
        """Context manager for source database sessions"""
        session = self.get_source_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def analytics_session_scope(self):
        """Context manager for analytics database sessions"""
        session = self.get_analytics_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def execute_source_query(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Execute a SQL query on source database and return results as DataFrame
        Used for reading investment data (portfolios, transactions, etc.)
        """
        try:
            logger.info("Executing source database query", query_preview=query[:100])
            
            with self.source_engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
                
            logger.info("Source query executed successfully", row_count=len(df))
            return df
            
        except Exception as e:
            logger.error("Source query execution failed", error=str(e), query=query)
            raise
    
    async def execute_analytics_query(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Execute a SQL query on analytics database and return results as DataFrame
        Used for reading stored analysis results, KPIs, etc.
        """
        try:
            logger.info("Executing analytics database query", query_preview=query[:100])
            
            with self.analytics_engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
                
            logger.info("Analytics query executed successfully", row_count=len(df))
            return df
            
        except Exception as e:
            logger.error("Analytics query execution failed", error=str(e), query=query)
            raise
    
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        For backward compatibility - defaults to source database
        """
        return await self.execute_source_query(query, params)
    
    async def save_analysis_result(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Save analysis results to analytics database
        
        Args:
            table_name: Target table name
            data: Data to save
        """
        try:
            # Convert data to DataFrame if it's not already
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                df = pd.DataFrame(data)
            
            # Save to analytics database
            with self.analytics_engine.connect() as conn:
                df.to_sql(table_name, conn, if_exists='append', index=False)
            
            logger.info("Analysis result saved", table=table_name, records=len(df))
            
        except Exception as e:
            logger.error("Failed to save analysis result", 
                        table=table_name, error=str(e))
            raise
    
    async def get_table_data(
        self,
        table_name: str,
        filters: Dict[str, Any] = None,
        limit: int = None,
        columns: List[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve data from a specific table with optional filtering
        
        Args:
            table_name: Name of the table to query
            filters: Dictionary of column filters
            limit: Maximum number of rows to return
            columns: Specific columns to select
            
        Returns:
            DataFrame with table data
        """
        try:
            # Check if table is active
            if not self.is_table_active(table_name):
                logger.warning("Attempted to access inactive table", table=table_name)
                return pd.DataFrame()
            
            # Build query
            select_columns = ", ".join(columns) if columns else "*"
            query = f"SELECT {select_columns} FROM {table_name}"
            
            # Add filters
            params = {}
            if filters:
                where_conditions = []
                for i, (column, value) in enumerate(filters.items()):
                    param_name = f"param_{i}"
                    where_conditions.append(f"{column} = :{param_name}")
                    params[param_name] = value
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            # Add limit
            if limit:
                query += f" ORDER BY (SELECT NULL) OFFSET 0 ROWS FETCH NEXT {limit} ROWS ONLY"
            
            return await self.execute_query(query, params)
            
        except Exception as e:
            logger.error("Failed to retrieve table data", error=str(e), table=table_name)
            raise
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with schema information
        """
        try:
            query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
            """
            
            df = await self.execute_query(query, {"table_name": table_name})
            
            schema = {
                "table_name": table_name,
                "columns": df.to_dict("records"),
                "row_count": await self._get_table_row_count(table_name)
            }
            
            return schema
            
        except Exception as e:
            logger.error("Failed to retrieve table schema", error=str(e), table=table_name)
            raise
    
    async def _get_table_row_count(self, table_name: str) -> int:
        """Get approximate row count for a table"""
        try:
            query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            df = await self.execute_query(query)
            return int(df.iloc[0]["row_count"])
        except:
            return 0
    
    async def get_available_tables(self) -> List[str]:
        """Get list of all available tables in the database"""
        try:
            query = """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
            
            df = await self.execute_query(query)
            return df["TABLE_NAME"].tolist()
            
        except Exception as e:
            logger.error("Failed to retrieve available tables", error=str(e))
            raise
    
    def is_table_active(self, table_name: str) -> bool:
        """Check if a table is currently active for analysis"""
        return self._active_tables.get(table_name, True)
    
    async def set_table_active(self, table_name: str, active: bool) -> None:
        """Set table active/inactive status"""
        self._active_tables[table_name] = active
        
        # Persist to configuration table if it exists
        try:
            query = """
            MERGE TableConfiguration AS target
            USING (SELECT :table_name AS table_name, :active AS is_active) AS source
            ON target.table_name = source.table_name
            WHEN MATCHED THEN
                UPDATE SET is_active = source.is_active, updated_at = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (table_name, is_active, created_at, updated_at)
                VALUES (source.table_name, source.is_active, GETDATE(), GETDATE());
            """
            
            with self.sync_engine.connect() as conn:
                conn.execute(text(query), {"table_name": table_name, "active": active})
                conn.commit()
                
        except Exception as e:
            logger.warning("Could not persist table configuration", error=str(e))
    
    async def get_active_tables(self) -> List[str]:
        """Get list of currently active tables"""
        return [table for table, active in self._active_tables.items() if active]
    
    async def _initialize_table_config(self) -> None:
        """Initialize table configuration from database"""
        try:
            # Load existing configuration
            query = "SELECT table_name, is_active FROM TableConfiguration"
            df = await self.execute_query(query)
            
            for _, row in df.iterrows():
                self._active_tables[row["table_name"]] = bool(row["is_active"])
                
            logger.info("Table configuration loaded", active_tables=len(self.get_active_tables()))
            
        except Exception:
            # If configuration table doesn't exist, set all core tables as active
            for table in db_settings.core_tables:
                self._active_tables[table] = True
            
            logger.info("Using default table configuration")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics for both databases"""
        try:
            # Test connections
            connection_status = await self.test_connections()
            
            stats = {
                "source_database": {
                    "type": settings.SOURCE_DB_TYPE,
                    "name": settings.SOURCE_DB_NAME,
                    "connection_status": "connected" if connection_status["source"] else "disconnected",
                    "tables": []
                },
                "analytics_database": {
                    "type": "postgresql", 
                    "name": settings.ANALYTICS_DB_NAME,
                    "connection_status": "connected" if connection_status["analytics"] else "disconnected",
                    "tables": []
                }
            }
            
            # Get source database table information
            if connection_status["source"]:
                try:
                    available_tables = await self.get_available_source_tables()
                    stats["source_database"]["table_count"] = len(available_tables)
                    stats["source_database"]["tables"] = available_tables[:10]  # First 10 tables
                except Exception as e:
                    logger.warning("Failed to get source database stats", error=str(e))
            
            # Get analytics database table information
            if connection_status["analytics"]:
                try:
                    analytics_tables = await self.get_available_analytics_tables()
                    stats["analytics_database"]["table_count"] = len(analytics_tables)
                    stats["analytics_database"]["tables"] = analytics_tables
                except Exception as e:
                    logger.warning("Failed to get analytics database stats", error=str(e))
            
            return stats
            
        except Exception as e:
            logger.error("Failed to retrieve database statistics", error=str(e))
            return {
                "error": str(e), 
                "source_database": {"connection_status": "error"},
                "analytics_database": {"connection_status": "error"}
            }
    
    async def get_available_source_tables(self) -> List[str]:
        """Get list of available tables in source database"""
        try:
            if settings.SOURCE_DB_TYPE == "postgresql":
                query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            elif settings.SOURCE_DB_TYPE == "sqlserver":
                query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """
            else:  # mysql
                query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            
            df = await self.execute_source_query(query)
            return df.iloc[:, 0].tolist()  # First column contains table names
            
        except Exception as e:
            logger.error("Failed to retrieve available source tables", error=str(e))
            return []
    
    async def get_available_analytics_tables(self) -> List[str]:
        """Get list of available tables in analytics database"""
        try:
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            
            df = await self.execute_analytics_query(query)
            return df.iloc[:, 0].tolist()
            
        except Exception as e:
            logger.error("Failed to retrieve available analytics tables", error=str(e))
            return []