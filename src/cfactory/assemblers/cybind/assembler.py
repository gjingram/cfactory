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

from cfactory.assemblers.cybind.cybind_writers import (
        PxdWriter,
        PyxWriter
        )

module_registry = {}
header_map = {}

def register_module(cybind_module: "CybindModule") -> bool:
    if cybind_module in module_registry.values():
        cfg.cfactory_logger.bind(color="red").opt(colors=True).error(
            f"Cybind moodule \"{cybind_module.module_name}\"" +
            "already registered"
            )
        sys.exit(-1)
    module_registry[cybind_module.module_name] = cybind_module
    return

def map_headers() -> None:
    for cybind_module in module_registry.values():
        for module_header in cybind_module.module_headers:
            header_map[module_header] = cybind_module.module_name
    return


class CybindModule(object):

    def __init__(
            self,
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
        self.pyx = self.out_file_noext + ".pyx"
        self.pxd = self.out_file_noext + ".pxd"
        self.pyx_writer = PyxWriter(
                self.module_name,
                self.pyx,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section
                )
        self.pxd_writer = PxdWriter(
                self.module_name,
                self.pxd,
                license_section=self.assembler.license_section,
                footer_section=self.assembler.footer_section
                )
        register_module(self)
        return

    @classmethod
    def from_header(
            cls,
            assembler: "CybindAssembler",
            header: str) -> "CythonModule":
        module_name = (
                os.path.relpath(header, assembler.package_dir).replace(
                    os.sep, "."
                    )
                )
        return CybindModule(module_name, assembler)


    def write_files(self) -> None:
        tic = time.perf_counter()
        self.pxd_writer.write_file()
        self.pyx_writer.write_file()
        toc = time.perf_counter()
        cfg.cfactory_logger.info(
                f"{self.module_name}.pxd/pyx written in {toc - tic} [s]"
                )
        return


class CybindAssembler(assembler.FinishAssembler):

    def __init__(self, package_name: str):
        super().__init__(
                "cybind." + package_name,
                singleton=False
                )

        self.package_name = package_name
        self.cybind_out = "cybind"
        self.package_dir = ""
        self._file_globs = []

        self.license_file = ""
        self.include_paths = []
        self.libs = []

        self.license_section = None
        self.footer_section = None
        self._headers = []
        self._cybind_modules = []

        self._ccm_rlevel = assembler.CCMRecursionLvel.INHERITED

        return

    def _add_file(self, file_: str) -> None:
        if "*" in file:
            self._headers.extend(glob.glob(file_))
        else:
            self._headers.append(file_)
        return

    def add_files(self, files: Union[str, List[str]]) -> None:
        if type(files) is str:
            self._add_file(files)
        elif type(files) is list:
            for file_ in files:
                self._add_file(file_)
        return

    def pre_assemble(self) -> None:
        self.source_dependencies = set(self._headers)
        for header in self._headers:
            module = CybindModule.from_header(self, header)
            module
            self._cybind_modules.append(
                    CybindModule.from_header(self, header)
                    )



