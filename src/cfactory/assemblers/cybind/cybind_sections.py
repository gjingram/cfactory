import os
import time

from . import paths
from cfactory.utils.wheezy_section import WheezySection
import cfactory.utils.file_writer as fw
import cfactory.assemblers.cybind.cybind as cybind


template_path = os.path.join(
        paths.cybind_top,
        "templates"
        )


class HeaderSection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "cybind_header")
        WheezySection.__init__(self, "cybind_header.template")
        self.search_path = [template_path]
        self.author = "Anonymous"
        self.header = ""
        self.ctx = {}
        return

    def make_context(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> dict:
        self.ctx["mtime"] = time.localtime()
        self.ctx["author"] = self.author
        self.ctx["binds"] = self.header
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(self.ctx)
        return


class ImportSection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "import")
        WheezySection.__init__(self, "import_section.template")
        self.cimports = []
        self.pyimports = []
        self.ctx = {}
        return

    def make_context(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> dict:
        self.ctx["cimports"] = self.cimports
        self.ctx["pyimports"] = self.pyimports
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(self.ctx)
        return


class PxdBodySection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "pxd_body")
        WheezySection.__init__(self, "pxd_body.template")
        self.header = ""
        self.namespace = None
        self.ctx = {}
        return

    def make_context(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> dict:
        self.ctx["header"] = self.header
        self.ctx["namespace"] = self.namespace
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(self.ctx)
        return


class PyxBodySection(fw.FileSection, WheezySection):

    def __init__(self):
        fw.FileSection.__init__(self, "pyx_body")
        WheezySection.__init__(self, "pyx_body.template")
        self.header = ""
        self.namespace = None
        self.ctx = {}
        return

    def make_context(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> dict:
        self.ctx["header"] = self.header
        self.ctx["namespace"] = self.namespace
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(self.ctx)
        return




