import logging
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))

def get_logger(logger_name, logger_file):
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        log_file = os.path.join(project_root, 'logs', logger_file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        logger.propagate = False

    return logger