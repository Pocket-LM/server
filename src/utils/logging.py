import logging
import sys
from logging import Formatter, StreamHandler, getLogger

# Define the format for the logs
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create a formatter
formatter = Formatter(log_format)

# Create a stream handler to output logs to stdout
stream_handler = StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

# Configure the root logger
root_logger = getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)

# Configure the uvicorn logger
uvicorn_logger = getLogger("uvicorn")
uvicorn_logger.handlers.clear()
uvicorn_logger.setLevel(logging.INFO)
uvicorn_logger.addHandler(stream_handler)
uvicorn_logger.propagate = False

# Uvicorn access logger
uvicorn_access_logger = getLogger("uvicorn.access")
uvicorn_access_logger.handlers.clear()
uvicorn_access_logger.setLevel(logging.INFO)
uvicorn_access_logger.addHandler(stream_handler)
uvicorn_access_logger.propagate = False

# Uvicorn error logger
uvicorn_error_logger = getLogger("uvicorn.error")
uvicorn_error_logger.handlers.clear()
uvicorn_error_logger.setLevel(logging.INFO)
uvicorn_error_logger.addHandler(stream_handler)
uvicorn_error_logger.propagate = False


# Configure the watchfiles logger
watchfiles_logger = getLogger("watchfiles")
watchfiles_logger.handlers.clear()
watchfiles_logger.setLevel(logging.INFO)
watchfiles_logger.addHandler(stream_handler)
watchfiles_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    This function returns a logger instance with the specified name.
    """
    logger = getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
