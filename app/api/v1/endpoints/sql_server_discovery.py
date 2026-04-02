"""
Real SQL Server Table Discovery - Investment Data Analysis Agent
===============================================================

Endpoints para descubrir las tablas REALES de SQL Server y sus estructuras.
Similar a como descubrimos que GD_Fondos tiene columnas Portfolio, PshipID, FN_Activo.

Author: Investment Data Analysis Agent
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, date
from sqlalchemy import text, inspect
import structlog

from app.database.connection import DatabaseManager

router = APIRouter(prefix="/discover", tags=["SQL Server Discovery"])
logger = structlog.get_logger(__name__)


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    return db_manager


@router.get("/tables", summary="🔍 Discover all SQL Server tables")
async def discover_tables(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Descubrir TODAS las tablas disponibles en SQL Server GD_EG_001
    """
    try:
        # Query para obtener todas las tablas del esquema
        query = text("""
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_SCHEMA NOT IN ('sys', 'INFORMATION_SCHEMA', 'db_accessadmin', 'db_backupoperator', 'db_datareader', 'db_datawriter', 'db_ddladmin', 'db_denydatareader', 'db_denydatawriter', 'db_owner', 'db_securityadmin')
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            tables = []
            
            for row in result:
                table_info = {
                    "Schema": row.TABLE_SCHEMA,
                    "TableName": row.TABLE_NAME,
                    "FullName": f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}" if row.TABLE_SCHEMA != 'dbo' else row.TABLE_NAME,
                    "TableType": row.TABLE_TYPE
                }
                tables.append(table_info)
        
        logger.info("Tablas de SQL Server descubiertas", total_tables=len(tables))
        
        return {
            "database": "GD_EG_001",
            "total_tables": len(tables),
            "tables": tables
        }
        
    except Exception as e:
        logger.error("Error descubriendo tablas SQL Server", error=str(e))
        raise HTTPException(status_code=500, detail=f"Table discovery error: {str(e)}")


@router.get("/table-structure/{table_name}", summary="🔎 Discover table structure") 
async def discover_table_structure(
    table_name: str,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Descubrir la estructura completa de una tabla específica
    """
    try:
        # Query para obtener columnas de la tabla
        columns_query = text("""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """)
        
        # Query para obtener una muestra de datos (TOP 3)
        sample_query = text(f"SELECT TOP 3 * FROM {table_name}")
        
        with db_manager.get_source_session() as session:
            # Obtener estructura de columnas
            columns_result = session.execute(columns_query, {"table_name": table_name})
            columns = []
            
            for row in columns_result:
                column_info = {
                    "ColumnName": row.COLUMN_NAME,
                    "DataType": row.DATA_TYPE,
                    "IsNullable": row.IS_NULLABLE,
                    "MaxLength": row.CHARACTER_MAXIMUM_LENGTH,
                    "Precision": row.NUMERIC_PRECISION,
                    "Scale": row.NUMERIC_SCALE
                }
                columns.append(column_info)
            
            # Obtener muestra de datos
            try:
                sample_result = session.execute(sample_query)
                sample_columns = sample_result.keys()
                sample_rows = sample_result.fetchall()
                
                sample_data = []
                for row in sample_rows:
                    sample_record = dict(zip(sample_columns, row))
                    # Convert any datetime objects to strings
                    for key, value in sample_record.items():
                        if hasattr(value, 'isoformat'):
                            sample_record[key] = value.isoformat() 
                    sample_data.append(sample_record)
            except Exception as e:
                sample_data = f"Error getting sample data: {str(e)}"
        
        logger.info("Estructura de tabla descubierta", table_name=table_name, columns=len(columns))
        
        return {
            "table_name": table_name,
            "total_columns": len(columns), 
            "columns": columns,
            "sample_data": sample_data
        }
        
    except Exception as e:
        logger.error("Error descubriendo estructura de tabla", table_name=table_name, error=str(e))
        raise HTTPException(status_code=500, detail=f"Table structure discovery error: {str(e)}")


@router.get("/find-positions", summary="🎯 Find positions-related tables")
async def find_positions_tables(
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Buscar tablas que contengan datos de posiciones/holdings
    """
    try:
        # Buscar tablas que contengan palabras relacionadas con posiciones
        query = text("""
        SELECT DISTINCT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND (
            TABLE_NAME LIKE '%posic%' OR 
            TABLE_NAME LIKE '%holding%' OR 
            TABLE_NAME LIKE '%portfolio%' OR
            TABLE_NAME LIKE '%asset%' OR
            TABLE_NAME LIKE '%position%' OR
            TABLE_NAME LIKE 'GD_%'
        )
        ORDER BY TABLE_NAME
        """)
        
        with db_manager.get_source_session() as session:
            result = session.execute(query)
            tables = [row.TABLE_NAME for row in result]
        
        logger.info("Tablas relacionadas con posiciones encontradas", tables=tables)
        
        return {
            "search_criteria": "positions, holdings, portfolio, asset, GD_*", 
            "matching_tables": tables,
            "total_found": len(tables)
        }
        
    except Exception as e:
        logger.error("Error buscando tablas de posiciones", error=str(e))
        raise HTTPException(status_code=500, detail=f"Positions search error: {str(e)}")