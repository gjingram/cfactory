import os
import sys
import shutil
from pathlib import Path
from typing import Optional
import time

import cfactory.__config__.cfactory_config as cfg
import pdb


class FileSection(object):

    def __init__(self, section_name: str):
        self.name = section_name
        self.section_text = ""
        self.subsections = []
        self.wrap_fn = None
        pass

    def write_section(
            self,
            file_object: "TextIOWrapper",
            extras: Optional[dict] = None) -> None:
        if self.section_text == "":
            return
        write_text = ""
        if self.wrap_fn is not None:
            write_text = self.wrap_fn(self.section_text, extras=extras)
        else:
            write_text = self.section_text
        file_object.write(write_text)
        return

    def add_text(self, text: str) -> bool:
        if self.section_text != "":
            cfg.cfactory_logger.bind(color="orange").opt(colors=True).warn(
                    f"{self.section_name} text already set."
                    )
            return False
        self.section_text = text
        return True

    def add_subsection(self, sub: "FileSection") -> None:
        if sub is None:
            return
        self.subsections.append(sub)
        return

    def resolve_section_text(self, extras: Optional[dict] = None) -> None:
        pass


class LicenseSection(FileSection):

    def __init__(self, license_file: str):
        super().__init__("license")
        self.license_path = license_file
        return

    def resolve_section_text(self) -> None:
        if not os.path.exists(self.license_path):
            return
        with open(self.license_path, "r") as lfile:
            self.section_text = lfile.read()
        return


class HeaderSection(FileSection):

    def __init__(self):
        super().__init__("header")
        return

    def resolve_section_text(self, **extras) -> None:
        for sub in self.subsections:
            sub.resolve_section_text()
            self.section_text += sub.section_text
            self.section_text += "\n"
        return


class FileWriter(object):

    def __init__(
            self,
            displayname: str,
            path: str):
        self.displayname = displayname
        self.file_path = path
        self.file_dir = os.path.dirname(self.file_path)
        if not os.path.exists(self.file_dir):
            Path(self.file_dir).mkdir(parents=True)
        self.extras = {}
        self.file_sections = []
        return

    def add_file_section(self, section: FileSection) -> None:
        self.file_sections.append(section)
        return

    def initialize_writer(self) -> None:
        pass

    def write_file(self) -> None:
        self.initialize_writer()
        with open(self.file_path, "w") as file_:
            for section in self.file_sections:
                section.resolve_section_text()
                section.write_section(file_, self.extras)
        return


class CodeWriter(FileWriter):

    def __init__(
            self,
            displayname: str,
            path: str,
            license_section: Optional[FileSection] = None,
            license_file: Optional[str] = None,
            license_text: Optional[str] = None,
            footer_section: Optional[FileSection] = None,
            footer_text: Optional[str] = None):
        super().__init__(displayname, path)

        self.header = HeaderSection()
        license_sub = None
        if license_section is not None:
            license_sub = license_section
        elif license_file is not None:
            license_sub = LicenseSection(license_file)
        else:
            license_sub = FileSection("license")
            if license_text is not None:
                license_sub.section_text = license_text
        self.header.add_subsection(license_sub)
        self.add_file_section(self.header)

        self.footer = None
        if footer_section is not None:
            self.footer = footer_section
        else:
            self.footer = FileSection("footer")
            if footer_text is not None:
                self.footer.section_text = footer_text

        self.long_comment_wrapper = None
        self.short_comment_wrapper = None

        return

    def initialize_writer(self) -> None:
        self.add_file_section(self.footer)
        return
