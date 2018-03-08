import logging
import sys

_debug = False


def set_debug(value):
    global _debug

    _debug = value


def logger_factory(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(name)s] %(asctime)s > %(levelname)-10s %(message)s', '%Y-%m-%d %H:%M:%S')

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


def bar(label, value, m = 32):
    """Represent a value as a filled bar.

    Args:
        label (str): A label for the bar.
        value (float): The value to represent, in the range [0,1]
        m (int): The length of the bar in characters.

    Example:
        >>> bar("X", 0.5)
        X ████████████████░░░░░░░░░░░░░░░░
    """
    size = int(value * m)
    bar_string = "█" * size + "░" * (m - size)
    return "{label} {bar} {value:>3}".format(label = label, bar = bar_string, value = int(value * 100))


def debug(text):
    global _debug

    if not _debug: return

    print(text)

def move_up(n):
    global _debug

    if not _debug: return
    sys.stdout.write("\033[{}A".format(n))
