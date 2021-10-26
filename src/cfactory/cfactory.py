import argparse
import os
import sys
import time
from pathlib import Path
from warnings import warn
from typing import (
        Tuple,
        List
        )

import cfactory.__config__.cfactory_config as cfg
import cfactory.factory as factory
import cfactory.utils.file_sys as fs

import ccmodel.ccm as ccm
import ccmodel.reader as ccm_reader

cfact_cl = argparse.ArgumentParser(
        description="CFactory Command Line Interface"
        )
cfact_cl.add_argument(
        "-r",
        "--root",
        default=os.getcwd(),
        help="Directory to start cfscript search from"
        )
cfact_cl.add_argument(
        "-v",
        "--verbosity",
        help="Verbosity level",
        type=int,
        choices={0, 1, 2},
        default=0
        )
cfact_cl.add_argument(
        "--clear-cache",
        help="Delete cfactory cache and replace",
        action="store_true",
        default=False
        )
cfact_cl.add_argument(
        "--clear-ccm",
        help="Delete ccm cache and replace",
        action="store_true",
        default=False
        )
cfact_cl.add_argument(
        "--force",
        help="Update regardless of modification status",
        action="store_true",
        default=False
        )
cfact_cl.add_argument(
        "--force-ccm",
        help="Update CCModel state regardless of modification status",
        action="store_true",
        default=False
        )
cfact_cl.add_argument(
        "--ccm-pretty",
        help="Make parsed CCModel state files human-readable",
        action="store_true",
        default=False
        )
cfact_cl.add_argument(
        "--mode",
        help="CFactory execution mode",
        choices={"cfactory", "ccmodel"},
        default="cfactory"
        )

cfactory_mode = "cfactory"
def process_command_line() -> None:
    global cfactory_mode
    opts = cfact_cl.parse_args()
    factory.root = fs.path_from_fs_root(opts.root)
    factory.clear_ccm = opts.clear_ccm
    factory.force_ccm = opts.force_ccm
    factory.pretty_ccm = opts.ccm_pretty
    cfactory_mode = opts.mode
    return

def find_cfscripts() -> None:
    for root, dirs, files in os.path.walk(factory.root):
        for file_ in files:
            if os.path.basename(file_) == "cfscript.py":
                factory.cfscripts.append(file_)
    return

def exec_cfscripts() -> None:
    for cfscript in factory.cfscripts:
        with fs.cd(os.path.dirname(cfscript)):
            exec(
                    compile(
                        open(cfscript, "r").read(),
                        cfscript,
                        "exec"
                        ),
                    globals()
                    )
    return

def main() -> None:
    if not factory.cfscript_in_root():
        # Logger error
        sys.exit(-1)
    find_cfscripts()
    exec_cfscripts()
    if cfactory_mode == "cfactory":
        factory.factory_assemble()
    elif cfactory_mode = "ccmodel":
        factory.ccmodel_assemble()
    else:
        # Logger error
        sys.exit(-1)
    return

def main_cl() -> None:
    process_command_line()
    main()
    return
