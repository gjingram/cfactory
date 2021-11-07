import os

from . import paths
from cfactory.utils.wheezy_section import WheezySection
import cfactory.utils.file_writer as fw


template_path = os.path.join(
        paths.cybind_top,
        "templates"
        )


class HeaderSection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "cybind_header")
        WheezySection.__init__(self, "cybind_header.template")
        self.search_path = [template_path]
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(**extras)
        return


class ImportSection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "import")
        WheezySection.__init__(self, "import_section.template")
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(**extras)
        return


class PxdBodySection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "pxd_body")
        WheezySection.__init__(self, "pxd_body.template")
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(**extras)
        return


class PyxBodySection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "pyx_body")
        WheezySection.__init__(self, "pyx_body.template")
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(**extras)
        return




