import os
import sys
from pathlib import Path
from typing import (
        Optional
        )
import subprocess

from breathe import __version__
from breathe.project import (
        ProjectInfo
        )
from breathe.parser import DoxygenParserFactory
from breathe.finder.factory import FinderFactory
from breathe.renderer.filter import FilterFactory
from breathe.parser import DoxygenParserFactory

from sphinx.application import Sphinx
from xml.dom import Node

import cfactory.breathe.doxy_cfg as doxy_cfg


class BreatheModels(object):

    def __init__(self, ff: FilterFactory, node: Node):
        self.namespaces = []
        self.classes = []
        self.functions = []
        self.types = []

        self.filter_factory = ff
        self.node = node

        return




class BreatheArgs(object):

    def __init__(self):
        self.destdir = os.getcwd()
        self.force = False
        self.members = False
        self.dryrun = False
        self.notoc = False
        self.suffix = ".rst"
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
            if var in mods.keys():
                var_use = mods[var]
            else:
                var_use = var
            print(f"{var_use}: {val}")
        return


class BreatheParser(object):

    def __init__(self, module_path: str, doc_dir: str = "docs"):
        
        self.module_path = module_path
        self.module_name = os.path.split(module_path)[-1]
        self.doc_dir = doc_dir
        self.source_dir = os.path.join(module_path, doc_dir, "source")
        self.build_dir = os.path.join(module_path, doc_dir, "build")
        self.doctree_dir = os.path.join(
                self.build_dir,
                "doctree"
                )

        mkdir = lambda path: return Path(path).mkdir(
                parents=True,
                exist_ok=True
                )

        mkdir(self.source_dir)
        mkdir(self.build_dir)
        mkdir(self.doctree_dir)

        self.app = Sphinx(
                self.source_dir,
                self.source_dir,
                self.build_dir,
                self.doctree_dir
                )
        self.project_info = ProjectInfo(
                self.app,
                self.module_name,
                self.module_path,
                self.source_dir,
                self.module_path
                )
        self.parser_factory = DoxygenParserFactory(self.app)
        self.index_parser = self.parser_factory.create_index_parser()
        self.compound_parser = self.parser_factory.create_compound_parser(
                self.project_info
                )

        self.index_file = os.path.join(self.source_dir, "index.xml")
        self.compound_files = {
                x.split(".")[0]: None for x in os.listdir(self.source_dir) if
                x != "index.xml"
                }

        self.finder_factory = FinderFactory(self.app, self.parser_factory)
        self.filter_factory = 
        self.args = BreatheArgs()
        self.models = BreatheModels()

        self.cfg = doxy_cfg.DoxyConfig()
        self.cfg_path = os.path.join(self.doc_dir, "doxy_cfg")
        self.cfg_dir = self.doc_dir

        self._index_found = False
        self._doxy_cfg_found = False

        self.delete_index = False
        self.delete_doxy_cfg = False
        self.allow_doxy_exec = True
        self.allow_write_cfg = True
        self.force = False
        self.filter_factory = BreatheFilterFactory(self.sphinx)
        return

    def _check_for_index(self) -> None:
        if os.path.exists(self.index_file) and Path(self.index_file).is_file():
            self._index_found = True
        if self._index_found and self.delete_index:
            os.remove(self.index_file)
            self._index_found = False
            if not self.allow_doxy_exec:
                raise FileNotFoundError(self.index_file)
        return

    def _check_for_doxy_cfg(self) -> None:
        if os.path.exists(self.cfg_path) and Path(self.cfg_path).is_file():
            self._doxy_cfg_found = True
        if self._doxy_cfg_found and self.delete_doxy_cfg:
            self.cfg.delete_doxy_cfg()
            self._doxy_cfg_found = False
            if not self.allow_write_cfg:
                raise FileNotFoundError(self.cfg_path)
        return


    def parse(self) -> None:
        
        self._check_for_index()
        self._check_for_doxy_cfg()

        if not self._index_found:
            cd_back = os.getcwd()
            os.chdir(self.source_dir)
            subprocess.run([
                "doxygen",
                self.cfg_path
                ]
                )
            os.chdir(cd_back)
        if not self._doxy_cfg_found:
            self.cfg.write_doxy_cfg(self.cfg_path)

        self.index = self.xml_parser(self.index_file)

        return
















