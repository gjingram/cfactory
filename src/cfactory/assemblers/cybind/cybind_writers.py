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


class CyWriter(pyfiles.PyFileWriter):

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
                license_section,
                None,
                None,
                footer_section,
                None
                )
        
        self._ccm = factory.ccm
        self._ccms = {}
        self._headers_in_module = []
        self.writeables = {}
        return

    def add_header(self, header: str) -> None:
        if header not in self._headers_in_module:
            self._headers_in_module.append(header)
        return

    def resolve_writeables(self) -> None:
        for header in self._headers_in_module:
            ccms = self._ccm[header]
            self._ccms[header] = ccms
            t_unit = ccms.translation_unit

            writeable = {]
            writeable["linkage_specs"] = t_unit.linkage_specs
            writeable["classes"] = t_unit.classes
            writeable["variables"] = t_unit.variables
            writeable["functions"] = t_unit.functions
            writeable["namespaces"] = t_unit.namespaces
            writeable["typedefs"] = t_unit.typedefs
            self.writeables[header] = writeable

        return

    def make_header_section(self) -> None:
        self.add_file_section(self.header)
        return self.header

    def make_import_section(self) -> None:
        out = fw.FileSection("import")
        self.file_sections.append(out)
        return out

    def make_class_section(self) -> None:
        out = fw.FileSection("classes")
        self.file_sections.append(out)
        return out

    def make_variable_section(self) -> None:
        out = fw.FileSection("variables")
        self.file_sections.append(out)
        return out

    def make_function_section(self) -> None:
        out = fw.FileSection("functions")
        self.file_sections.append(out)
        return out


class PxdWriter(CyWriter):

    def __init__(
            self,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
        super().__init__(
                path,
                license_section,
                footer_section,
                )
        return


class PyxWriter(CyWriter):

    def __init__(
            self,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
        super().__init__(
                path,
                license_section,
                footer_section,
                )
        return



