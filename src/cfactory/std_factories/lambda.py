import typing
import pdb
from abc import ABC, abstractmethod

import illuminate.__config__.illuminate_config as il_cfg
from illuminate.code_models.parse_object import ParseObjectDependency,
    python_var_pattern, ParseObject

import re
import illuminate.code_models.code_utils as code_utils
from mako.template import Template
from mako.lookup import TemplateLookup


class LambdaExpression(metaclass=ABC):

    def __init__(self):

        self._captures = []
        self._parameters = []
        self._specifiers = []
        self.exception = None
        self._attr = []
        self.return_type = None

        return

    @property
    def captures(self) -> typing.List[ParseObject]:
        return self._captures

    @property.setter
    def captures(self, cap: typing.Union[ParseObject, typing.List[ParseObject]]) -> None:
        return code_utils.add_to_list(self._captures, cap, ParseObject)

    @property
    def parameters(self) -> typing.List[str]:
        return self._parameters

    @property.setter
    def parameters(self, param: typing.Union[str, typing.List[str]]) -> None:
        return code_utils.add_to_list(self._parameters, param, str)

    @property
    def specifiers(self) -> typing.List[str]:
        return self._specifiers

    @property.setter
    def specifiers(self, spec: typing.Union[str, typing.List[str]]) -> None:
        return code_utils.add_to_list(self._specifiers, spec, str)

    @property
    def attr(self) -> typing.List[str]:
        return self_attr

    @property.setter
    def attr(self, attr: typing.Union[str, typing.List[str]]) -> None:
        return code_utils.add_to_list(self._attr, attr, str)

    @abstractmethod
    def render(self) -> str:
        pass


class MakoLambda(LambdaExpression):

    def __init__(self, template: Template, mako_def: str = None, 
            lookup: Template = TemplateLookup(directories=il_cfg.lookup_directories)):
        LambdaExpression.__init__(self)

        self._template = lookup.get_template(template)

        return

    def render(self) -> str:
        return self._template.render(expr=self)


def __print_token_list__(toks: typing.List[str], delim: str, brackets: str = None) -> str:
    string_out = ""
    if brackets is not None:
        string_out += brackets[0]
    string_out = f"{toks[0]}{delim} "
    for tok in toks[1:-1]:
        string_out += f"{tok}{delim} "
    string_out += toks[-1]
    if brackets is not None:
        string_out += brackets[1]
    return string_out


class FStringLambda(LambdaExpression, metaclass=ABC):

    def __init__(self):
        LambdaExpression.__init__(self)

        return

    def render(self) -> str:
        string_out = (
                f"{__print_token_list__(self.captures, ',', '[]')}"
                f"{__print_token_list__(self.parameters, ',', '()'}"
                f" {self.specifiers}"
                f" {self.exception}"
                f" {self.attr} "
                f"-> {self.return_type} {"
                )
        string_out = f"""{string_out}
    {self.render_body()}
}"""

        return string_out

    @abstractmethod
    def render_body(self):
        pass
