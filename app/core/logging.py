import logging


LOG_FORMAT = "[%(name)s]: %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=LOG_FORMAT)


def get_logger(component: str) -> logging.Logger:
    return logging.getLogger(component)
