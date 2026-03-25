"""
Human-readable logger for Fins API and Django application.
Provides colored console output with timestamps and context information.
"""

import logging
import time
from datetime import datetime
from typing import Optional, Any, Dict
import sys


class ColorCodes:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FinsLogger:
    """
    Human-readable logger for Fins project with colored output and timing support.
    Designed for both API requests/responses and Django operations.
    """
    
    def __init__(self, name: str, output_file: Optional[str] = None):
        """
        Initialize logger.
        
        Args:
            name: Logger name/identifier
            output_file: Optional file path to also log to file
        """
        self.name = name
        self.output_file = output_file
        self.operation_stack = []  # Track nested operations for indentation
        self.timing_stack = {}  # Track operation timings
        
    def _timestamp(self) -> str:
        """Get current timestamp in HH:MM:SS format"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _indent(self) -> str:
        """Get indentation based on operation depth"""
        return "  " * len(self.operation_stack)
    
    def _format_message(self, level: str, message: str, color: str) -> str:
        """Format a log message with timestamp and color"""
        timestamp = self._timestamp()
        indent = self._indent()
        
        # Create formatted message
        formatted = f"{color}[{timestamp}] {indent}[{level}] {message}{ColorCodes.ENDC}"
        return formatted
    
    def _write_log(self, message: str):
        """Write log message to console and file if configured"""
        print(message, file=sys.stdout)
        sys.stdout.flush()
        
        if self.output_file:
            try:
                # Strip ANSI codes for file logging
                clean_msg = self._strip_ansi(message)
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(clean_msg + '\n')
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
    
    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def info(self, message: str, **kwargs):
        """Log info level message"""
        if kwargs:
            message = self._format_kwargs(message, kwargs)
        formatted = self._format_message("INFO", message, ColorCodes.CYAN)
        self._write_log(formatted)
    
    def success(self, message: str, **kwargs):
        """Log success message (green)"""
        if kwargs:
            message = self._format_kwargs(message, kwargs)
        formatted = self._format_message("✓ SUCCESS", message, ColorCodes.GREEN)
        self._write_log(formatted)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message"""
        if kwargs:
            message = self._format_kwargs(message, kwargs)
        formatted = self._format_message("⚠ WARNING", message, ColorCodes.YELLOW)
        self._write_log(formatted)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error level message"""
        if kwargs:
            message = self._format_kwargs(message, kwargs)
        if exception:
            message += f"\n{self._indent()}  Exception: {type(exception).__name__}: {str(exception)}"
        formatted = self._format_message("✗ ERROR", message, ColorCodes.RED)
        self._write_log(formatted)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message"""
        if kwargs:
            message = self._format_kwargs(message, kwargs)
        formatted = self._format_message("DEBUG", message, ColorCodes.BLUE)
        self._write_log(formatted)
    
    def section(self, title: str):
        """Log a section header"""
        formatted = f"{ColorCodes.BOLD}{ColorCodes.HEADER}\n{'='*60}\n{title}\n{'='*60}{ColorCodes.ENDC}"
        self._write_log(formatted)
    
    def subsection(self, title: str):
        """Log a subsection header"""
        indent = self._indent()
        separator = "-" * (50 - len(indent))
        formatted = f"{ColorCodes.BOLD}{ColorCodes.YELLOW}{indent}{title} {separator}{ColorCodes.ENDC}"
        self._write_log(formatted)
    
    def start_operation(self, operation_name: str, **context):
        """
        Start tracking an operation (increases indent level).
        
        Args:
            operation_name: Name of the operation
            **context: Additional context to log (e.g., endpoint, request_id)
        """
        self.operation_stack.append(operation_name)
        operation_id = len(self.operation_stack)
        self.timing_stack[operation_id] = time.time()
        
        context_str = ""
        if context:
            context_str = " " + " | ".join(f"{k}={v}" for k, v in context.items())
        
        message = f"▶ Starting: {operation_name}{context_str}"
        formatted = self._format_message("START", message, ColorCodes.BLUE)
        self._write_log(formatted)
        return operation_id
    
    def end_operation(self, operation_id: Optional[int] = None, status: str = "completed"):
        """
        End operation tracking and log duration.
        
        Args:
            operation_id: ID of operation (auto-determined if None)
            status: 'completed', 'failed', 'skipped'
        """
        if not self.operation_stack:
            return
        
        if operation_id is None:
            operation_id = len(self.operation_stack)
        
        operation_name = self.operation_stack.pop()
        
        # Calculate duration
        start_time = self.timing_stack.get(operation_id, time.time())
        duration = time.time() - start_time
        duration_str = f"{duration:.3f}s" if duration >= 0.001 else f"{duration*1000:.1f}ms"
        
        # Determine color based on status
        if status == "failed":
            color = ColorCodes.RED
            symbol = "✗"
        elif status == "skipped":
            color = ColorCodes.YELLOW
            symbol = "⊘"
        else:
            color = ColorCodes.GREEN
            symbol = "✓"
        
        message = f"{symbol} {operation_name} {status} ({duration_str})"
        formatted = self._format_message("END", message, color)
        self._write_log(formatted)
        
        if operation_id in self.timing_stack:
            del self.timing_stack[operation_id]
    
    def api_request(self, method: str, endpoint: str, **params):
        """
        Log an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **params: Request parameters to log
        """
        op_id = self.start_operation(
            f"API {method}",
            endpoint=endpoint,
            params=len(params) if params else 0
        )
        
        # Log parameters if present
        if params:
            param_str = self._format_dict(params)
            self.debug(f"Request parameters: {param_str}")
        
        return op_id
    
    def api_response(self, op_id: int, status_code: int, response_size: int = 0, **data):
        """
        Log an API response.
        
        Args:
            op_id: Operation ID from api_request()
            status_code: HTTP status code
            response_size: Size of response in bytes
            **data: Response data summary
        """
        status_category = "completed" if 200 <= status_code < 300 else "failed"
        
        size_str = f" | size={response_size}B" if response_size else ""
        
        # Log status info before ending operation
        if 200 <= status_code < 300:
            self.info(f"API Response: {status_code}{size_str}")
        elif 400 <= status_code < 500:
            self.warning(f"API Response: {status_code}{size_str}")
        else:
            self.error(f"API Response: {status_code}{size_str}")
        
        if data:
            self.debug(f"Response summary: {self._format_dict(data)}")
        
        self.end_operation(op_id, status=status_category)
    
    def database_operation(self, operation: str, query_type: str, **details):
        """Log database operation"""
        op_id = self.start_operation(f"DB {query_type}", operation=operation)
        if details:
            self.debug(f"Details: {self._format_dict(details)}")
        return op_id
    
    def validation_result(self, item: str, is_valid: bool, errors: Optional[list] = None):
        """
        Log a validation result.
        
        Args:
            item: Item being validated
            is_valid: Whether validation passed
            errors: List of validation errors if any
        """
        if is_valid:
            self.success(f"{item} validation passed")
        else:
            error_str = " | ".join(errors) if errors else "Unknown error"
            self.error(f"{item} validation failed: {error_str}")
    
    def performance_metric(self, metric_name: str, value: float, unit: str = "", threshold: Optional[float] = None):
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of metric
            value: Metric value
            unit: Unit of measurement
            threshold: Optional threshold for alerting
        """
        value_str = f"{value:.2f}{unit}" if unit else str(value)
        message = f"{metric_name}: {value_str}"
        
        if threshold and value > threshold:
            self.warning(f"{message} (exceeds threshold: {threshold}{unit})")
        else:
            self.info(message)
    
    @staticmethod
    def _format_kwargs(message: str, kwargs: Dict[str, Any]) -> str:
        """Format kwargs into message"""
        if not kwargs:
            return message
        kwargs_str = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        return f"{message} [{kwargs_str}]"
    
    @staticmethod
    def _format_dict(data: Dict[str, Any]) -> str:
        """Format dictionary for logging"""
        if not data:
            return "{}"
        items = ", ".join(f"{k}={v}" for k, v in data.items())
        return f"{{{items}}}"


# Global logger instances
_api_logger = None
_django_logger = None


def get_api_logger(output_file: Optional[str] = None) -> FinsLogger:
    """Get or create the API logger"""
    global _api_logger
    if _api_logger is None:
        log_file = output_file or "logs/api.log"
        _api_logger = FinsLogger("API", output_file=log_file)
    return _api_logger


def get_django_logger(output_file: Optional[str] = None) -> FinsLogger:
    """Get or create the Django logger"""
    global _django_logger
    if _django_logger is None:
        log_file = output_file or "logs/django.log"
        _django_logger = FinsLogger("DJANGO", output_file=log_file)
    return _django_logger


def get_logger(name: str = "fins", output_file: Optional[str] = None) -> FinsLogger:
    """Get a generic logger instance"""
    return FinsLogger(name, output_file=output_file)
