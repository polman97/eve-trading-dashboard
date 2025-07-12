import logging

def get_logger(name: str = "app", log_file: str = "app.log") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers in case of repeated imports
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(message)s"
        ))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(message)s"
        ))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger