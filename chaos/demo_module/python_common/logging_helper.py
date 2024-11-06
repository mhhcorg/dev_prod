import logging
import sys

def get_logger(filepath = 'log.log', level = logging.DEBUG):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    """ Screen Debug Log """
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    """ File Log """
    file_handler = logging.FileHandler(filepath)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # To make sure re-runs 
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

    return logger

if __name__ == "__main__":
    import os
    logger = get_logger(os.path.dirname(os.path.realpath(__file__)) + '/log.log')
    logger.info('Test')