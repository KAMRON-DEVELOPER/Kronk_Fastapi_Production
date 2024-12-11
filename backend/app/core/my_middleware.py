import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import logging
from pythonjsonlogger import jsonlogger
import sys
from collections import defaultdict
from logging.handlers import RotatingFileHandler

metrics_data = defaultdict(int)

logger = logging.getLogger("kronk-logger")

stdout = logging.StreamHandler(stream=sys.stdout)

fileHandler = RotatingFileHandler("logs.txt", backupCount=2, maxBytes=400)
jsonFileHandler = RotatingFileHandler("json_logs.json", backupCount=2, maxBytes=400)

stdout.setLevel(logging.INFO)
fileHandler.setLevel(logging.INFO)

fmt = jsonlogger.JsonFormatter(
    "%(name)s %(asctime)s %(levelname)s %(filename)s %(lineno)s %(process)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
)
stdoutFmt = logging.Formatter(
    "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
)

stdout.setFormatter(fmt)
fileHandler.setFormatter(stdoutFmt)
jsonFileHandler.setFormatter(fmt)

logger.addHandler(stdout)
logger.addHandler(fileHandler)
logger.addHandler(jsonFileHandler)
logger.setLevel(logging.INFO)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            metrics_data["total_requests"] += 1
            start_time = time.perf_counter()
            response = await call_next(request)
            stop_time = time.perf_counter()

            logging.info(f"{request.method} {request.url} - Status: {response.status_code} - Time: {stop_time - start_time:.4f}s")
        except Exception as e:
            metrics_data["total_errors"] += 1
            logging.error(f"Error processing request: {e}")
