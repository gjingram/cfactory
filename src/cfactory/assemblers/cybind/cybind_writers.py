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
import pdb


class CybindWriter(pyfile.PyFileWriter):

    def __init__(
            self,
            header: str,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
            author: str = ""
            ):

        display_path = os.path.relpath(
                path,
                cybind.cybind_project_root
                )
        display_root, file_name = os.path.split(display_path)
        displayname = ".".join(
                [
                *display_root.split(os.sep),
                file_name
                ]
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
      
        self.author = author
        self.header_path = header
        self.header.add_subsection(
                HeaderSection()
                )
        self.import_section = ImportSection()

        return

    def write_file(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> None:
        cybind_header = self.header.subsections[-1]
        cybind_header.header = os.path.relpath(
                self.header_path,
                cybind.cybind_project_root
                )
        cybind_header.author = self.author
        cybind_header.make_context(t_unit)
        self.import_section.make_context(t_unit)
        fw.CodeWriter.write_file(self)
        return


class PxdWriter(CybindWriter):

    def __init__(
            self,
            header: str,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
            author: str = ""
            ):
        super().__init__(
                header,
                path,
                license_section=license_section,
                footer_section=footer_section,
                author=author
                )
        self.pxd_body = PxdBodySection()
        self.add_file_section(self.pxd_body)
        return

    def write_file(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> None:
        self.pxd_body.header = self.header_path
        self.pxd_body.namespace = t_unit
        self.pxd_body.make_context(t_unit)
        for ns in t_unit.namespaces:
            new_sub = PxdBodySection()
            new_sub.header = self.header_path
            new_sub.namespace = ns
            new_sub.make_context(t_unit)
            self.pxd_body.add_subsection(
                    new_sub
                    )
        CybindWriter.write_file(self, t_unit)
        return


class PyxWriter(CybindWriter):

    def __init__(
            self,
            header: str,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            footer_section: Optional[fw.FileSection] = None,
            author: str = ""
            ):
        super().__init__(
                header,
                path,
                license_section=license_section,
                footer_section=footer_section,
                author=author
                )
        self.pyx_body = PyxBodySection()
        self.add_file_section(self.pyx_body)
        return

    def write_file(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> None:
        self.pyx_body.header = self.header
        self.pyx_body.namespace = t_unit
        self.pyx_body.make_context(t_unit)
        for ns in t_unit.namespaces:
            new_sub = PyxBodySection()
            new_sub.header = self.header_path
            new_sub.namespace = ns
            new_sub.make_context(t_unit)
            self.pyx_body.add_subsection(
                    new_sub
                    )
        CybindWriter.write_file(self, t_unit)
        return
