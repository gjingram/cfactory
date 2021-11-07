import os
import sys
import shutil
import time
import glob
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
            assembler: "CybindAssembler"):

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
        self.pyx_writer = PyxWriter(
                self.pyx,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section
                )
        self.pxd_writer = PxdWriter(
                self.pxd,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section
                )
        pdb.set_trace()
        cybind.register_module(self)
        return

    @classmethod
    def from_header(
            cls,
            assembler: "CybindAssembler",
            header: str) -> "CythonModule":
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
                assembler
                )


    def write_files(self) -> None:
        tic = time.perf_counter()
        self.pxd_writer.write_file()
        self.pyx_writer.write_file()
        toc = time.perf_counter()
        cfg.cfactory_logger.info(
                f"{self.module_name}.pxd/pyx written in {toc - tic} [s]"
                )
        return


class CybindAssembler(assembler.FinishStage):

    def __init__(
            self,
            package_name: str,
            package_dir: str = os.getcwd(),
            out_dir: str = "cybind"):
        super().__init__(
                "cybind." + package_name,
                singleton=False
                )

        self.package_name = package_name
        self.cybind_out = os.path.join(
                package_dir,
                out_dir
                )
                
        self.package_dir = package_dir
        self._file_globs = []

        self.license_file = ""
        self.include_paths = []
        self.libs = []

        self.license_section = None
        self.footer_section = None
        self._headers = []
        self._cybind_modules = []

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
        pdb.set_trace()
        if type(files) is str:
            self._add_file(files)
        elif type(files) is list:
            for file_ in files:
                self._add_file(file_)
        self.source_dependencies = set(self._headers)
        return

    def pre_assemble(self) -> None:
        for header in self._headers:
            module = CybindModule.from_header(self, header)
            self._cybind_modules.append(
                    module
                    )
        return



