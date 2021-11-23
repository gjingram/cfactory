import os
import time

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.ext.code import CodeExtension
from wheezy.template.loader import FileLoader

from . import paths
import cfactory.utils.file_writer as fw
import cfactory.assemblers.cybind.cybind as cybind
import pdb


template_path = os.path.join(
        paths.cybind_top,
        "templates"
        )
template_engine = Engine(
        loader=FileLoader([template_path]),
        extensions=[
            CoreExtension(),
            CodeExtension()
            ]
        )
template_engine


class WheezyCybind(object):

    def __init__(self, template: str):
        self.template = template_engine.get_template(
                template
                )
        return

    def template_eval(self, ctx: dict) -> str:
        return self.template.render(ctx)



class HeaderSection(fw.FileSection, WheezyCybind):

    def __init__(self):
        fw.FileSection.__init__(self, "cybind_header")
        WheezyCybind.__init__(self, "cybind_header.template")
        self.search_path = [template_path]
        self.author = "Anonymous"
        self.header = ""
        self.ctx = {}
        return

    def make_context(
            self,
            t_unit: "ccmodel.code_models.variants.TranslationUnitDecl"
            ) -> dict:
        self.ctx["mtime"] = time.strftime(
                "%Y/%m/%d %H:%M:%S",
                time.localtime()
                )
        self.ctx["author"] = self.author
        self.ctx["binds"] = self.header
        return

    def resolve_section_text(self, **extras: dict) -> None:
        self.section_text = self.template_eval(self.ctx)
        return


class ImportSection(fw.FileSection, WheezyCybind):

    def __init__(self):
        fw.FileSection.__init__(self, "import")
        WheezyCybind.__init__(self, "import_section.template")
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


class PxdBodySection(fw.FileSection, WheezyCybind):

    def __init__(self):
        fw.FileSection.__init__(self, "pxd_body")
        WheezyCybind.__init__(self, "pxd_body.template")
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


class PyxBodySection(fw.FileSection, WheezyCybind):

    def __init__(self):
        fw.FileSection.__init__(self, "pyx_body")
        WheezyCybind.__init__(self, "pyx_body.template")
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
