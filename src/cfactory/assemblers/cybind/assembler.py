import os
import sys
import shutil
import time
import glob
from pathlib import Path
from typing import (
        List,
        Union,
        Optional
        )

import cfactory.assemblers.assembler as assembler
import cfactory.factory as factory
import cfactory.utils.file_writer as fw
import cfactory.utils.file_sys as fs
import cfactory.__config__.cfactory_config as cfg

import cfactory.assemblers.cybind.cybind as cybind
from cfactory.assemblers.cybind.cybind_writers import (
        PxdWriter,
        PyxWriter
        )
import pdb


class CybindModule(object):

    def __init__(
            self,
            module_header: str,
            module_name: str,
            assembler: "CybindAssembler",
            author: str = ""):

        self.module_author = author
        self.module_name = module_name
        self.module_path_noext = (
                self.module_name.replace(
                    ".",
                    os.sep
                    )
                )
        self.assembler = assembler
        self.out_file_noext = (
                os.path.join(
                    self.assembler.cybind_out,
                    self.module_path_noext.lstrip(os.sep)
                    )
                )
        self.header = module_header
        self.pyx = self.out_file_noext + ".pyx"
        self.pxd = self.out_file_noext + ".pxd"
        self.out_dir = os.path.dirname(self.pyx)

        self.pyx_writer = PyxWriter(
                self.header,
                self.pyx,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section,
                author=self.module_author
                )
        self.pxd_writer = PxdWriter(
                self.header,
                self.pxd,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section,
                author=self.module_author
                )

        cybind.register_module(self)

        self.ccms = factory.ccm[self.header]
        self.cimport = []
        self.pyimport = []

        # TODO: Some sort of import resolver that parses
        # types and determines cimport/import statements
        # required at the top of the cybind files-- e.g.,
        # it might see an Eigen array and map it to a
        # numpy.ndarray, requiring a cimport/import numpy
        # statement.
        self.import_resolver = None
        return

    @classmethod
    def from_header(
            cls,
            assembler: "CybindAssembler",
            header: str,
            author: str = "") -> "CythonModule":
        if assembler.package_dir == "":
            assembler.package_dir = (
                    factory.project_root if factory.project_root != "" else
                    os.getcwd()
                    )
        module_reldir = os.path.dirname(
                os.path.relpath(
                    header,
                    assembler.package_dir
                    )
                ).replace(
                        os.sep,
                        '.'
                        )
        module_basename = os.path.basename(header).split('.')[0]
        module_name = module_reldir + "." + module_basename
        return CybindModule(
                header,
                module_name,
                assembler,
                author=author
                )

    def resolve_imports(self) -> None:
        #self.import_resolver.resolve_imports(self.ccms)
        #self.cimport.extend(self.import_resolver.cimports)
        #self.pyimport.extend(self.import_resolver.pyimports)
        self.cimport.extend(
                [
                    cybind.header_map[x] for x in self.ccms.includes if
                    x in cybind.header_map
                    ]
                )

        # TODO: import resolver ought to also check includes for existing
        # cython standard cimports to handle things like the standard
        # library.

        self.pyx_writer.import_section.cimports = self.cimport
        self.pxd_writer.import_section.cimports = self.cimport
        self.pyx_writer.import_section.pyimports = self.pyimport
        self.pxd_writer.import_section.pyimports = self.pyimport
        return

    def write_files(self) -> None:
        self.resolve_imports()
        t_unit = self.ccms.translation_unit
        tic = time.perf_counter()
        self.pxd_writer.write_file(t_unit)
        self.pyx_writer.write_file(t_unit)
        toc = time.perf_counter()
        cfg.cfactory_logger.info(
                f"{self.module_name}.pxd/pyx written in {toc - tic} [s]\n"
                )
        return


class CybindAssembler(assembler.FinishStage):

    def __init__(
            self,
            package_name: str,
            package_dir: str = os.getcwd(),
            out_dir: str = "cybind",
            author: str = ""):
        super().__init__(
                "cybind." + package_name,
                singleton=False
                )

        self.author = author
        self.package_name = package_name
        self.cybind_out = os.path.join(
                package_dir,
                out_dir
                )

        if not os.path.exists(self.cybind_out):
            Path(self.cybind_out).mkdir(parents=True)
                
        self.package_dir = package_dir
        self._file_globs = []

        self.license_file = ""
        self.include_paths = []
        self.libs = []

        self.license_section = None
        self.footer_section = None
        self._headers = []
        self._cybind_modules = []
        self._cpp_namespaces = []
        self._package_ccms = []

        self._ccm_rlevel = assembler.CCMRecursionLevel.INHERITED

        return

    def _add_file(self, file_: str) -> None:
        if "*" in file_:
            self._headers.extend(
                    [
                        os.path.abspath(x) for x in
                        glob.glob(file_)
                        ]
                    )
        else:
            self._headers.append(os.path.abspath(file_))
        return

    def add_files(self, files: Union[str, List[str]]) -> None:
        if type(files) is str:
            self._add_file(files)
        elif type(files) is list:
            for file_ in files:
                self._add_file(file_)
        self.source_dependencies = set(self._headers)
        return

    def find_namespaces(self) -> None:
        for header in self._headers:


    def pre_assemble(self) -> None:
        for header in self._headers:
            module = CybindModule.from_header(
                    self,
                    header,
                    author=self.author)
            self._cybind_modules.append(
                    module
                    )
        return

    def assemble(self) -> None:
        for module in self._cybind_modules:
            module.write_files()
        return
