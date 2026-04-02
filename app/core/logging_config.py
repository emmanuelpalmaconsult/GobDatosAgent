"""
Logging configuration for Investment Data Analysis Agent
Configures structured logging with rich console output and file rotation.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from rich.console import Console
from rich.logging import RichHandler

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    Sets up both console and file logging with proper formatting.
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True,
                tracebacks_show_locals=True
            ),
            logging.handlers.RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=settings.LOG_MAX_SIZE,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding="utf-8"
            )
        ]
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level and timestamp
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            
            # Add contextual information
            add_app_context,
            
            # Format for console or JSON
            structlog.dev.ConsoleRenderer() if settings.DEBUG 
            else structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def add_app_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add application-specific context to log events.
    
    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary to modify
        
    Returns:
        Modified event dictionary with additional context
    """
    
    # Add application information
    event_dict["app"] = "investment-data-agent"
    event_dict["version"] = "1.0.0"
    event_dict["environment"] = settings.ENVIRONMENT
    
    # Add database context if available
    if hasattr(settings, 'SQL_SERVER_DATABASE'):
        event_dict["database"] = settings.SQL_SERVER_DATABASE
    
    return event_dict


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Financial operations logging utilities
def log_financial_operation(
    logger: structlog.stdlib.BoundLogger,
    operation: str,
    portfolio_id: str = None,
    amount: float = None,
    currency: str = None,
    **kwargs
) -> None:
    """
    Log financial operations with standardized format.
    
    Args:
        logger: The logger instance
        operation: Type of financial operation
        portfolio_id: Portfolio identifier
        amount: Transaction amount
        currency: Currency code
        **kwargs: Additional context
    """
    
    context = {
        "operation_type": "financial",
        "operation": operation,
        **kwargs
    }
    
    if portfolio_id:
        context["portfolio_id"] = portfolio_id
    if amount:
        context["amount"] = amount
    if currency:
        context["currency"] = currency
    
    logger.info("Financial operation executed", **context)


def log_analysis_operation(
    logger: structlog.stdlib.BoundLogger,
    analysis_type: str,
    record_count: int = None,
    duration: float = None,
    **kwargs
) -> None:
    """
    Log analysis operations with performance metrics.
    
    Args:
        logger: The logger instance
        analysis_type: Type of analysis performed
        record_count: Number of records analyzed
        duration: Operation duration in seconds
        **kwargs: Additional context
    """
    
    context = {
        "operation_type": "analysis",
        "analysis_type": analysis_type,
        **kwargs
    }
    
    if record_count is not None:
        context["record_count"] = record_count
    if duration is not None:
        context["duration_seconds"] = round(duration, 3)
        context["performance"] = "slow" if duration > 5.0 else "normal"
    
    logger.info("Analysis operation completed", **context)


def log_export_operation(
    logger: structlog.stdlib.BoundLogger,
    export_type: str,
    destination: str,
    file_path: str = None,
    record_count: int = None,
    **kwargs
) -> None:
    """
    Log export operations to BI tools.
    
    Args:
        logger: The logger instance
        export_type: Type of export (powerbi, datastudio, python)
        destination: Export destination
        file_path: Output file path
        record_count: Number of records exported
        **kwargs: Additional context
    """
    
    context = {
        "operation_type": "export",
        "export_type": export_type,
        "destination": destination,
        **kwargs
    }
    
    if file_path:
        context["file_path"] = file_path
    if record_count is not None:
        context["record_count"] = record_count
    
    logger.info("Export operation completed", **context)