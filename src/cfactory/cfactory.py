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
import pdb

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

def process_command_line() -> None:
    opts = cfact_cl.parse_args()
    factory.root = fs.path_from_fs_root(opts.root)
    factory.clear_ccm = opts.clear_ccm
    factory.force_ccm = opts.force_ccm
    factory.pretty_ccm = opts.ccm_pretty
    factory.cfactory_mode = opts.mode
    factory.cfactory_verbosity = opts.verbosity
    return

def find_cfscripts() -> None:
    for root, dirs, files in os.walk(factory.root):
        for file_ in files:
            if os.path.basename(file_) == "cfscript.py":
                factory.cfscripts.append(
                        os.path.join(
                            root,
                            file_
                            )
                        )
    return

def exec_cfscripts() -> None:
    for cfscript in factory.cfscripts:
        with fs.cd(os.path.dirname(cfscript)):
            cfscript_file = open(cfscript, "r")
            exec(
                    compile(
                        cfscript_file.read(),
                        cfscript,
                        "exec"
                        ),
                    globals()
                    )
            if cfscript == os.path.join(factory.root, "cfscript.py"):
                factory.ensure_abspaths()
                cfg.cfactor_logger = cfg.logger.bind(
                        cf_stage_log=True,
                        project_name=factory.project_name
                        )
            cfscript_file.close()
    return

def main() -> None:
    log = cfg.logger.bind(
            cf_stage_log=True
            )
    if factory.cfactory_verbosity:
        cfg.logger.enable("cfactory")
    if not factory.cfscript_in_root():
        log.bind(color="red").opt(colors=True).error(
                f"No cfscript.py in specified root: {factory.root}"
                )
        sys.exit(-1)
    find_cfscripts()
    cfg.cfactory_logger = cfg.logger.bind(
            cf_stage_log=True,
            project_name=factory.project_name
            )
    exec_cfscripts()
    if factory.cfactory_mode == "cfactory":
        factory.factory_assemble()
    elif factory.cfactory_mode == "ccmodel":
        factory.ccmodel_assemble()
    else:
        log.bind(color="red").opt(colors=True).error(
                f"Unrecognized cfactory mode: {factory.cfactory_mode}"
                )
        sys.exit(-1)
    return

def main_cl() -> None:
    process_command_line()
    main()
    return
