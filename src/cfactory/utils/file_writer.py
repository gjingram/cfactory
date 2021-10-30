import os
import sys
import shutil
import time

import cfactory.__config__.cfactory_config as cfg


class FileSection(object):

    def __init__(self, section_name: str):
        self.name = section_name
        self.section_text = ""
        pass

    def write_section(self, file_object: file) -> None:
        self.resolve_section_text()
        file_object.write(self.section_text)
        return

    def resolve_section_text(self) -> None:
        pass


class LicenseSection(FileSection):

    def __init__(self, license_file: str):
        super().__init__("license")
        self.license_path = license_file
        return

    def resolve_section_text(self) -> None:
        if self.license_path is None:
            return
        with open(self.license_path, "r") as lfile:
            self.section_text = lfile.read()
        return


class FileWriter(object):

    def __init__(
            self,
            displayname: str,
            path: str):
        self.displayname = displayname
        self.file_path = path
        self.file_sections = []
        self._file = None
        return

    def add_file_section(self, section: FileSection) -> None:
        self.file_sections.append(section)
        return

    def write_file(self) -> None:
        with open(self.file_path, "w") as file_:
            for section in self.file_sections:
                section.write_section(file_)
        return
