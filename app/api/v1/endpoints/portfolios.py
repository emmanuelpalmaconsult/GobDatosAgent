"""
Portfolio management endpoints
CRUD operations and analysis for investment portfolios.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import structlog
from datetime import datetime, date
import pandas as pd

from app.models.schemas import (
    Portfolio, PortfolioCreate, PortfolioUpdate, PortfolioSummary,
    BaseResponse, PaginationParams, DateRangeFilter
)
from app.database.connection import DatabaseManager
from app.core.logging_config import log_financial_operation

router = APIRouter()
logger = structlog.get_logger(__name__)


async def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager"""
    db_manager = DatabaseManager()
    await db_manager.connect()
    return db_manager


@router.get("/", response_model=List[Portfolio])
async def get_portfolios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    portfolio_type: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Retrieve list of portfolios with optional filtering
    """
    try:
        logger.info("Retrieving portfolios list", skip=skip, limit=limit)
        
        # Build filter conditions
        filters = {}
        if portfolio_type:
            filters["portfolio_type"] = portfolio_type
        if status:
            filters["status"] = status
        
        # Get portfolio data
        query = """
        SELECT 
            portfolio_id, portfolio_code, portfolio_name, portfolio_type,
            currency, inception_date, manager_name, benchmark, risk_profile,
            status, max_investment, min_investment, management_fee, performance_fee,
            created_at, updated_at
        FROM Portfolios
        WHERE 1=1
        """
        
        params = {}
        if filters:
            for i, (column, value) in enumerate(filters.items()):
                param_name = f"param_{i}"
                query += f" AND {column} = :{param_name}"
                params[param_name] = value
        
        query += f" ORDER BY portfolio_code OFFSET {skip} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        df = await db_manager.execute_query(query, params)
        
        # Convert to Portfolio models
        portfolios = []
        for _, row in df.iterrows():
            portfolio = Portfolio(
                portfolio_id=row["portfolio_id"],
                portfolio_code=row["portfolio_code"],
                portfolio_name=row["portfolio_name"],
                portfolio_type=row["portfolio_type"],
                currency=row["currency"],
                inception_date=row["inception_date"],
                manager_name=row.get("manager_name"),
                benchmark=row.get("benchmark"),
                risk_profile=row.get("risk_profile"),
                status=row["status"],
                max_investment=row.get("max_investment"),
                min_investment=row.get("min_investment"),
                management_fee=row.get("management_fee"),
                performance_fee=row.get("performance_fee"),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            portfolios.append(portfolio)
        
        logger.info("Portfolios retrieved successfully", count=len(portfolios))
        return portfolios
        
    except Exception as e:
        logger.error("Failed to retrieve portfolios", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolios: {str(e)}")


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: int,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Get specific portfolio by ID
    """
    try:
        query = """
        SELECT 
            portfolio_id, portfolio_code, portfolio_name, portfolio_type,
            currency, inception_date, manager_name, benchmark, risk_profile,
            status, max_investment, min_investment, management_fee, performance_fee,
            created_at, updated_at
        FROM Portfolios 
        WHERE portfolio_id = :portfolio_id
        """
        
        df = await db_manager.execute_query(query, {"portfolio_id": portfolio_id})
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        row = df.iloc[0]
        portfolio = Portfolio(
            portfolio_id=row["portfolio_id"],
            portfolio_code=row["portfolio_code"],
            portfolio_name=row["portfolio_name"],
            portfolio_type=row["portfolio_type"],
            currency=row["currency"],
            inception_date=row["inception_date"],
            manager_name=row.get("manager_name"),
            benchmark=row.get("benchmark"),
            risk_profile=row.get("risk_profile"),
            status=row["status"],
            max_investment=row.get("max_investment"),
            min_investment=row.get("min_investment"),
            management_fee=row.get("management_fee"),
            performance_fee=row.get("performance_fee"),
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        
        logger.info("Portfolio retrieved", portfolio_id=portfolio_id)
        return portfolio
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve portfolio", portfolio_id=portfolio_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    portfolio_id: int,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Get portfolio summary with key metrics
    """
    try:
        # Get basic portfolio information
        portfolio_query = """
        SELECT portfolio_id, portfolio_code, portfolio_name, portfolio_type
        FROM Portfolios 
        WHERE portfolio_id = :portfolio_id
        """
        
        portfolio_df = await db_manager.execute_query(portfolio_query, {"portfolio_id": portfolio_id})
        
        if portfolio_df.empty:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio_row = portfolio_df.iloc[0]
        
        # Calculate current portfolio value
        value_query = """
        SELECT 
            COALESCE(SUM(t.quantity * md.close_price), 0) as current_value
        FROM Transactions t
        INNER JOIN MarketData md ON t.asset_id = md.asset_id
        WHERE t.portfolio_id = :portfolio_id
        AND md.price_date = (
            SELECT MAX(price_date) 
            FROM MarketData md2 
            WHERE md2.asset_id = md.asset_id
        )
        AND t.transaction_type IN ('buy', 'sell')
        GROUP BY t.portfolio_id
        """
        
        value_df = await db_manager.execute_query(value_query, {"portfolio_id": portfolio_id})
        current_value = value_df.iloc[0]["current_value"] if not value_df.empty else 0
        
        # Get latest performance metrics
        performance_query = """
        SELECT TOP 1
            total_return, annualized_return, volatility, sharpe_ratio
        FROM Performance 
        WHERE portfolio_id = :portfolio_id
        ORDER BY calculation_date DESC
        """
        
        perf_df = await db_manager.execute_query(performance_query, {"portfolio_id": portfolio_id})
        
        performance_data = {}
        if not perf_df.empty:
            perf_row = perf_df.iloc[0]
            performance_data = {
                "total_return": perf_row.get("total_return"),
                "return_percentage": perf_row.get("annualized_return"),
                "volatility": perf_row.get("volatility"),
                "sharpe_ratio": perf_row.get("sharpe_ratio")
            }
        
        summary = PortfolioSummary(
            portfolio_id=portfolio_row["portfolio_id"],
            portfolio_code=portfolio_row["portfolio_code"],
            portfolio_name=portfolio_row["portfolio_name"],
            portfolio_type=portfolio_row["portfolio_type"],
            current_value=current_value,
            last_updated=datetime.utcnow(),
            **performance_data
        )
        
        logger.info("Portfolio summary retrieved", portfolio_id=portfolio_id)
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve portfolio summary", portfolio_id=portfolio_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio summary: {str(e)}")


@router.get("/{portfolio_id}/positions")
async def get_portfolio_positions(
    portfolio_id: int,
    as_of_date: Optional[date] = Query(None),
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Get current positions for a portfolio
    """
    try:
        # Use current date if not specified
        if not as_of_date:
            as_of_date = date.today()
        
        # Get current positions
        positions_query = """
        WITH PositionSummary AS (
            SELECT 
                t.asset_id,
                a.asset_code,
                a.asset_name,
                a.asset_type,
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
                ) as avg_cost,
                SUM(
                    CASE 
                        WHEN t.transaction_type = 'buy' THEN t.net_amount
                        WHEN t.transaction_type = 'sell' THEN -t.net_amount
                        ELSE 0
                    END
                ) as invested_amount
            FROM Transactions t
            INNER JOIN Assets a ON t.asset_id = a.asset_id
            WHERE t.portfolio_id = :portfolio_id
            AND t.transaction_date <= :as_of_date
            GROUP BY t.asset_id, a.asset_code, a.asset_name, a.asset_type
            HAVING SUM(
                CASE 
                    WHEN t.transaction_type = 'buy' THEN t.quantity
                    WHEN t.transaction_type = 'sell' THEN -t.quantity
                    ELSE 0
                END
            ) > 0
        ),
        CurrentPrices AS (
            SELECT DISTINCT
                md.asset_id,
                FIRST_VALUE(md.close_price) OVER (
                    PARTITION BY md.asset_id 
                    ORDER BY md.price_date DESC
                ) as current_price
            FROM MarketData md
            WHERE md.price_date <= :as_of_date
        )
        SELECT 
            ps.*,
            cp.current_price,
            (ps.current_quantity * cp.current_price) as current_value,
            (ps.current_quantity * cp.current_price - ps.invested_amount) as unrealized_pnl,
            ((ps.current_quantity * cp.current_price - ps.invested_amount) / ps.invested_amount * 100) as unrealized_pnl_pct
        FROM PositionSummary ps
        LEFT JOIN CurrentPrices cp ON ps.asset_id = cp.asset_id
        ORDER BY ps.current_quantity * cp.current_price DESC
        """
        
        params = {
            "portfolio_id": portfolio_id,
            "as_of_date": as_of_date
        }
        
        df = await db_manager.execute_query(positions_query, params)
        
        # Convert to list of dictionaries
        positions = df.to_dict("records") if not df.empty else []
        
        # Calculate portfolio totals
        total_value = sum(pos.get("current_value", 0) or 0 for pos in positions)
        total_invested = sum(pos.get("invested_amount", 0) or 0 for pos in positions)
        total_pnl = sum(pos.get("unrealized_pnl", 0) or 0 for pos in positions)
        
        result = {
            "portfolio_id": portfolio_id,
            "as_of_date": as_of_date.isoformat(),
            "positions": positions,
            "summary": {
                "position_count": len(positions),
                "total_invested": total_invested,
                "total_current_value": total_value,
                "total_unrealized_pnl": total_pnl,
                "total_return_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0
            }
        }
        
        logger.info("Portfolio positions retrieved", 
                   portfolio_id=portfolio_id, 
                   position_count=len(positions))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve portfolio positions", 
                    portfolio_id=portfolio_id, error=str(e))
        raise HTTPException(status_code=500, 
                          detail=f"Failed to retrieve portfolio positions: {str(e)}")


@router.post("/", response_model=Portfolio)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db_manager: DatabaseManager = Depends(get_db_manager)
):
    """
    Create a new portfolio
    """
    try:
        # Check if portfolio code already exists
        check_query = "SELECT COUNT(*) as count FROM Portfolios WHERE portfolio_code = :code"
        check_df = await db_manager.execute_query(check_query, {"code": portfolio.portfolio_code})
        
        if check_df.iloc[0]["count"] > 0:
            raise HTTPException(status_code=400, detail="Portfolio code already exists")
        
        # Insert new portfolio
        insert_query = """
        INSERT INTO Portfolios (
            portfolio_code, portfolio_name, portfolio_type, currency, inception_date,
            manager_name, benchmark, risk_profile, max_investment, min_investment,
            management_fee, performance_fee, status, created_at, updated_at
        )
        OUTPUT INSERTED.portfolio_id
        VALUES (
            :portfolio_code, :portfolio_name, :portfolio_type, :currency, :inception_date,
            :manager_name, :benchmark, :risk_profile, :max_investment, :min_investment,
            :management_fee, :performance_fee, 'active', GETDATE(), GETDATE()
        )
        """
        
        params = portfolio.dict()
        result_df = await db_manager.execute_query(insert_query, params)
        
        if result_df.empty:
            raise HTTPException(status_code=500, detail="Failed to create portfolio")
        
        new_portfolio_id = result_df.iloc[0]["portfolio_id"]
        
        # Log the operation
        log_financial_operation(
            logger,
            "portfolio_creation",
            portfolio_id=str(new_portfolio_id),
            portfolio_code=portfolio.portfolio_code
        )
        
        # Return the created portfolio
        return await get_portfolio(new_portfolio_id, db_manager)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create portfolio", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create portfolio: {str(e)}")