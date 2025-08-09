import os
import sys
from pathlib import Path
from typing import Optional

from breathe.apidoc import (
        recurse_tree,
        create_modules_toc_file,
        TYPEDICT
        )
from breathe import __version__
from breathe.parser import DoxygenParserFactory
from breathe.project import ProjectInfoFactory
from breathe.process import AutoDoxygenProcessHandle

from sphinx.application import Sphinx

from docutils.parsers.rst import Directive

import cfactory.breathe.doxy_cfg as doxy_cfg

def setup(app: Sphinx) -> None:
    breathe_parser = BreatheParse(app)


class BreatheArgs(object):

    def __init__(self):
        self.destdir = os.getcwd()
        self.force = False
        self.members = False
        self.dryrun = False
        self.notoc = False
        self.suffix = "rst"
        self.project = None
        self.outtypes = []
        self.quiet = False
        self.rootpath = os.getcwd()
        self.version = __version__
        return

    def ls_breathe_args(self) -> None:
        mods = {
                "destdir": "output_dir",
                "dryrun": "dry_run",
                "notoc": "no_toc",
                "outtypes": "generate"
                }
        for var, val in vars(self).items():
            var_use = ""
            if var in mods.keys():
                var_use = mods[var]
            else:
                var_use = var
            print(f"{var_use} (default = {val})")
        return


class BreatheParse(object):

    def __init__(self, app: Sphinx):

        self.app = app
        self.parser_factory = DoxygenParserFactory(self.app)
        self.project_info_factory = ProjectInfoFactory(self.app)

        self.args = BreatheArgs()
        self.doxy_config = doxy_cfg.DoxyConfig()

        return

    @property
    def output_dir(self) -> str:
        return self.args.destdir

    @output_dir.setter
    def output_dir(self, odir: str) -> None:
        self.args.destdir = odir
        return

    @property
    def force(self) -> bool:
        return self.args.force

    @force.setter
    def force(self, yes: bool) -> None:
        self.args.force = yes
        return

    @property
    def members(self) -> bool:
        return self.args.members

    @members.setter
    def members(self, yes: bool) -> None:
        self.args.members = yes
        return

    @property
    def dry_run(self) -> bool:
        return self.args.dryrun

    @dry_run.setter
    def dry_run(self, yes: bool) -> None:
        self.args.dryrun = yes
        return

    @property
    def no_toc(self) -> bool:
        return self.args.notoc

    @no_toc.setter
    def no_toc(self, yes: bool) -> None:
        self.args.notoc = yes
        return

    @property
    def suffix(self) -> str:
        return self.args.suffix

    @suffix.setter
    def suffix(self, suf: str) -> None:
        self.args.suffix = suf
        return

    @property
    def project(self) -> Optional["Project"]:
        return self.args.project

    @project.setter
    def project(self, proj: "Project") -> None:
        self.args.project = proj
        return

    @property
    def generate(self) -> bool:
        return self.args.generate

    @generate.setter
    def generate(self, yes: bool) -> None:
        self.args.generate = yes
        return

    @property
    def quiet(self) -> bool:
        return self.args.quiet

    @quiet.setter
    def quiet(self, yes: bool) -> None:
        self.args.quiet = yes
        return

    @property
    def rootpath(self) -> str:
        return self.args.rootpath

    @rootpath.setter
    def rootpath(self, path: str) -> None:
        self.args.rootpath = path
        return

    def check_breathe_args() -> None:
        if self.args.suffix.startswith("."):
            self.args.suffix = self.args.suffix[1:]
        if not os.path.isdir(self.args.rootpath):
            print(f"{self.args.rootpath} is not a directory", file=sys.stderr)
            sys.exit(1)
        if "index.xml" not in os.listdir(self.args.rootpath):
            print(f"{self.args.rootpath} does not contain index.xml",
                    file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(self.args.output_dir):
            if not self.args.dry_run:
                Path(self.args.output_dir).mkdir(parents=True, exist_ok=True)
        return

    def run(self, app: Sphinx) -> None:



    def breathe_process(self) -> None:
        self.args.rootpath = os.path.abspath(self.args.rootpath)
        recurse_tree(self.args)
        if not self.args.notoc:
            for key in self.args.outtypes:
                create_modules_toc_file(key, TYPEDICT[key], self.args)
        return

    def doxygen_process(self) -> None:



