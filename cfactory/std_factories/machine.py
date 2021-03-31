from clang import cindex, enumerations
import os
import sys
import typing
from abc import abstractmethod, ABC
from datetime import datetime
import functools

import illuminate.__config__.illuminate_config as il_cfg
import illuminate.std_factories.mako_global as mg
from illuminate.code_models.parse_object import ParseObject
from illuminate.code_models.header import HeaderObject
import illuminate.std_factories.common_filters as cf
import illuminate.std_factories.factory as fac


class Machine(object):

    def __init__(self, model_object: typing.Union[ParseObject, HeaderObject],
            factory: typing.Optional['fac.Factory']):

        self.factory = factory
        self.model_wrapper = fac.Factory.wrapped_object[model_object.qualified_id]
        self.scope_wrapper = fac.Factory.wrapped_object[model_object.scope.qualified_id] \
                if model_object.scope is not None else None
        self._type_check()
        self._writers = []
        self.factory = factory
        self.machine_registered_writers = []

        return

    @property
    def text(self) -> str:
        return self.execute_machine()

    def _type_check(self) -> None:
        if self.check_type is None:
            return

        if not isinstance(self.model_object, self.check_type):
            error_text = (f"{type(self).__name__} Error: Machine expects a code model",
                    f" of type {self.check_type.__name__}")
            raise TypeError(error_text)
        return

    def execute_machine(self) -> str:
        out = ""
        for writer in self._writers:
            out += writer()
        return out
