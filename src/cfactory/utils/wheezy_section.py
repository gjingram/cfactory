from typing import (
        Optional,
        List
        )

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader


class WheezySection(object):

    def __init__(
            self,
            search: List[str]):
        self.search_paths = search
        self.engine = None
        self.loaders = []
        self.extensions = []
        self.template = None
        return

    def find_and_load(self) -> None:
        self.engine = Engine(
                self.search_paths,
                self.loaders,
                self.extensions
                )
        self.template = self.engine.get_template(
                self.template
                )
        return

    def template_eval(self, ctx: dict) -> str:
        return self.template.render(ctx)
