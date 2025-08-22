import sys

from loguru import logger as loguru_logger


def setup_logger():
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | {extra}"
    )
    loguru_logger.remove()
    loguru_logger.add(sys.stderr, format=logger_format, level="TRACE")
    loguru_logger.debug("starting application...")

    return loguru_logger


logger = setup_logger()
