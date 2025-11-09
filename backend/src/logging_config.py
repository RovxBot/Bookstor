"""Central logging configuration for Bookstor."""
import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATEFMT = "%Y-%m-%dT%H:%M:%S"

logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)

# Reduce noise from external libraries
for noisy in ["httpx", "uvicorn.error", "uvicorn.access"]:
    logging.getLogger(noisy).setLevel(logging.WARNING)

logger = logging.getLogger("bookstor")
