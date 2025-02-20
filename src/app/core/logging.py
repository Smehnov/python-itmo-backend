import logging
import sys

def setup_logging():
    # Create logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    return logger

logger = setup_logging() 