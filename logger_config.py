import logging
import sys
from pathlib import Path

# Configure a clean log format
log_format = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Send log streaming data directly to the terminal stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)

# NEW: Also write logs to a file so we can review/grep after a test run
Path("logs").mkdir(exist_ok=True)
file_handler = logging.FileHandler("logs/cc_switchboard.log", encoding="utf-8")
file_handler.setFormatter(log_format)

# Initialize the CC core logger instance
logger = logging.getLogger("cc_switchboard")
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)  # NEW