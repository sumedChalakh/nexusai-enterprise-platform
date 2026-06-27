import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # quiet down noisy libraries so Loki isn't flooded with debug spam
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
