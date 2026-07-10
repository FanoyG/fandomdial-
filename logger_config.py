import logging
import sys

# Configure a clean log format
log_format = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Send log streaming data directly to the terminal stdout
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)

# Initialize the CC core logger instance
logger = logging.getLogger("cc_switchboard")
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)