import sys
import pathlib
import os
from loguru import logger
from warnings import warn

cfactory_top = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parents[0])

def cfactory_stage_log(record):
    return record["extra"]["stage_log"]

def cfactory_stage_fmt(record):
    color = record["extra"]["color"]
    fmt = "cfactory: {message}"
    if color != "":
        fmt = f"<{color}>" + fmt + f"</{color}>"
    return fmt

cf_log_config = {
        "handlers": [
            {"sink": sys.stdout, "format": cfactory_stage_fmt, "filter": cfactory_stage_log},
            ],
        "extra": {
            "project": "",
            "indent": "",
            "stage_log": False,
            "color": ""
            }
        }

logger.configure(**cf_log_config)
logger.disable("cfactory")

cfactory_logger = None
