import logging

logger = logging.getLogger(__name__)
logger_handler = logging.StreamHandler()
logger_handler.setLevel(logging.INFO)
logger_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logger.addHandler(logger_handler)
