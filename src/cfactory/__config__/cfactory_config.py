import sys
import pathlib
import os
from loguru import logger
from warnings import warn
import pdb

def cfactory_stage_log(record):
    return record["extra"]["cf_stage_log"]

def cfactory_stage_fmt(record):
    color = record["extra"]["color"]
    fmt = "cfactory: {message}"
    if color != "":
        fmt = f"<{color}>" + fmt + f"</{color}>"
    return fmt

cf_log_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": cfactory_stage_fmt,
                "filter": cfactory_stage_log
                },
            ],
        "extra": {
            "project": "",
            "indent": "",
            "cf_stage_log": False,
            "color": ""
            }
        }

if len(logger._core.handlers) == 0:
    logger.configure(**cf_log_config)
else:
    for hndlr in cf_log_config["handlers"]:
        logger.add(**hndlr)
    logger._core.extra.update(cf_log_config["extra"])

if 0 in logger._core.handlers:
    logger.remove(0)
logger.disable("cfactory")

cfactory_logger = None
