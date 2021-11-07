import os
import sys
import shutil
import time
from typing import (
        List,
        Union,
        Optional
        )

import cfactory.factory as factory
import cfactory.assemblers.cybind.cybind as cybind
import cfactory.utils.file_writer as fw
import cfactory.utils.pyfamily_file as pyfile
import cfactory.utils.file_sys as fs
import cfactory.__config__.cfactory_config as cfg
from cfactory.assemblers.cybind.cybind_sections import (
        HeaderSection,
        ImportSection,
        PxdBodySection,
        PyxBodySection
        )


class CybindWriter(pyfile.PyFileWriter):

    def __init__(
            self,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
            ):

        display_path = os.path.relpath(
                path,
                cybind.cybind_project_root
                )
        display_root, file_name = os.path.split(display_path)
        displayname = ".".join(
                *display_root.split(os.sep),
                file_name
                )
        super().__init__(
                displayname,
                path,
                license_section=license_section,
                license_file=None,
                license_text=None,
                footer_section=footer_section,
                footer_text=None
                )
        
        self._ccm = factory.ccm
        self._ccms = {}
        self._headers_in_module = []
        self.writeables = {}

        self.header.add_subsection(
                HeaderSection()
                )
        self.import_section = ImportSection()

        return

    def make_cybind_context(self, writeable: dict) -> dict:
        pass

    def add_header(self, header: str) -> None:
        if header not in self._headers_in_module:
            self._headers_in_module.append(header)
        return

    def resolve_writeables(self) -> None:
        for header in self._headers_in_module:
            ccms = self._ccm[header]
            self._ccms[header] = ccms
            t_unit = ccms.translation_unit

            writeable = {}
            writeable["linkage_specs"] = t_unit.linkage_specs
            writeable["classes"] = t_unit.classes
            writeable["variables"] = t_unit.variables
            writeable["functions"] = t_unit.functions
            writeable["namespaces"] = t_unit.namespaces
            writeable["typedefs"] = t_unit.typedefs
            self.writeables[header] = writeable

        return


class PxdWriter(CybindWriter):

    def __init__(
            self,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None
            ):
        super().__init__(
                path,
                license_section=license_section,
                footer_section=footer_section,
                )
        self.pxd_body = PxdBodySection()
        return


class PyxWriter(CybindWriter):

    def __init__(
            self,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None
            ):
        super().__init__(
                path,
                license_section=license_section,
                footer_section=footer_section,
                )
        self.pyx_body = PyxBodySection()
        return



