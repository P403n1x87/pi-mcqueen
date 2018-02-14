import logging

def logger_factory(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(name)s] %(asctime)s > %(levelname)-10s %(message)s', '%Y-%m-%d %H:%M:%S')

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
