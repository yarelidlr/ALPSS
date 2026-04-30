import logging


def setup_alpss_logger():
    logger = logging.getLogger("alpss")

    if not logger.handlers:  # no handlers = nothing configured yet
        # Standalone mode → set up a default
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = (
            False  # prevent duplicate output via root logger (e.g. in Jupyter)
        )

    # Otherwise (if processor already set things up) → just use its config
    return logger
