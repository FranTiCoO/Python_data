import logging


def configure_logging():
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        format='%(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)d]     %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.INFO,
    )


def get_logger(name=None):
    configure_logging()
    return logging.getLogger(name)


logger = get_logger(__name__)
