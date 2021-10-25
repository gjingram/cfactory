from illuminate.code_models.alias_objects import (TypeDefObject,
        TypeAliasObject, TemplateAliasObject)
from illuminate.code_models.class_object import ClassObject
from illuminate.code_models.directive_objects import (
        UsingNamespaceObject, UsingDeclarationObject)
from illuminate.code_models.enumeration import (EnumObject,
        EnumConstDeclObject)
from illuminate.code_models.function import FunctionObject
from illuminate.code_models.function_param import FunctionParamObject
from illuminate.code_models.member_function import MemberFunctionObject
from illuminate.code_models.member import MemberObject
from illuminate.code_models.template import TemplateObject
from illuminate.code_models.template_param import TemplateParamObject
from illuminate.code_models.union import UnionObject
from illuminate.code_models.variable import VariableObject

from illuminate.pybind.enumerations import ReturnValuePolicy
import warnings


class PybindOpt(object):

    def __init__(self, expose: bool = True):
        self.expose = False
        return


class VariableOpt(PybindOpt):

    def __init__(self, expose: bool = True,
                module_attr: bool = True):
        
        PybindOpt.__init__(self, expose)
        self._module_attr = True
        self._try_make_property = False

        if expose and not module_attr:
            self._try_make_property = True

        return

    @property
    def module_attr(self, is_it: bool) -> None:
        if is_it:
            self._try_make_wrappers = False
        self._module_attr = is_it
        return

    @module_attr.getter
    def module_attr(self) -> bool:
        return self._module_attr

    @property
    def try_make_property(self, do: bool) -> None:
        if do:
            self._module_attr = False
        self._try_make_property = do
        return

    @try_make_wrappers.getter(self) -> bool:
        return self._try_make_property


class MemberVariableOpt(PybindOpt):

    def __init__(self, expose: bool = True,
                try_make_getter: bool = False,
                try_make_setter: bool = False,
                using_getter: typing.Optional['MemberFunctionObject'] = None,
                using_setter: typing.Optional['MemberFunctionObject'] = None):
        
        PybindOpt.__init__(self, expose)
        self._try_make_getter = try_make_getter and using_getter is None
        self._try_make_setter = try_make_setter and using_setter is None
        self._using_getter = using_getter
        self._using_setter = using_setter
        return

    @property
    def try_make_getter(self, do: bool) -> None:
        if do:
            self._using_getter = None
        self._try_make_getter = do
        return

    @try_make_getter.getter
    def try_make_getter(self) -> bool:
        return self._try_make_getter

    @property
    def try_make_setter(self, do: bool) -> None:
        if do:
            self._using_setter = None
        self._try_make_setter = do
        return

    @try_make_setter.getter
    def try_make_setter(self) -> bool:
        return self._try_make_setter

    @property
    def using_getter(self, getter: typing.Optional['MemberFunctionObject']) -> None:
        if getter is None:
            self._using_getter = None
        else:
            self._using_getter = getter
            self._try_make_getter = False
        return

    @using_getter.getter
    def using_getter(self) -> typing.Optional['MemberFunctionObject']:
        return self._using_getter

    @property
    def using_setter(self, setter: typing.Optional['MemberFunctionObject']) -> None:
        if setter is None:
            self._using_setter = None
        else:
            self._using_setter = setter
            self._try_make_setter = False
        return

    @using_setter.getter
    def using_setter(self) -> typing.Optional['MemberFunctionObject']):
        return self._using_setter


class FunctionParamOpt(PybindOpt):

    def __init__(self, expose: bool = True,
                no_convert: bool = False,
                disallow_node: bool = False,
                no_kwarg: bool = False,
                ignore_default: bool =False,
                in_out: bool = False,
                is_args: bool = False,
                is_kwargs: bool = False):

        PybindOpt.__init__(self, expose)
        self.no_convert = no_convert
        self.disallow_none = disallow_none
        self.no_kwarg = no_kwarg
        self.ignore_default = ignore_defaults
        self.in_out = in_out
        self.is_args = is_args
        self.is_kwargs = is_kwargs

        return


class FunctionOpt(PybindOpt):

    def __init__(self, expose: bool = True,
                rvp: ReturnValuePolicy = ReturnValuePolicy.AUTOMATIC,
                keep_alive: typing.List[typing.Tuple] = [],
                scope_guards: typing.List = [],
                priority_overload: bool = False):

        PybindOpt.__init__(self, expose)
        self.rvp = ReturnValuePolicy.AUTOMATIC
        self.keep_alive = []
        self.scope_guards = []
        self.priority_overload = priority_overload
        return

class MemberFunctionOpt(FunctionOpt):

    def __property_warning__():
        warnings.warn("MemberFunctionOpt Warning: Member function has been declared as an anonymous getter/setter.")
        return

    def __init__(self, expose: bool = True,
                rvp: ReturnValuePolicy = ReturnValuePolicy.AUTOMATIC,
                keep_alive: typing.List[typing.Tuple] = [],
                scope_guards: typing.List = [],
                priority_overload: bool = False,
                factory_method: bool = False,
                property_getter: bool = False,
                property_setter: bool = False,
                property_refers_to: typing.Optional[str] = None):

        FunctionOpt.__init__(self, expose, rvp, keep_alive,
                scope_guards, priority_overload)

        self._property_getter = False
        self._property_setter = False
        if property_getter and property_setter:
            raise ValueError("MemberFunctionOpt Fatal: property getter and property setter are mutually exclusive options.")

        if property_getter or property_setter and property_refers_to is None:
            MemberFunctionOpt.__property_warning__()
        
        self.factory_method = factory_method
        self.property_getter = property_getter
        self.property_setter = property_setter
        self.property_refers_to = property_refers_to

        return

    @property
    def property_setter(self, is_it: bool) -> None:
        if is_it:
            property_getter = False
            property_setter = True
        if self.property_refers_to is None:
            MemberFunctionOpt.__property_warning__()
        return

    @property_setter.getter
    def property_setter(self) -> bool:
        return self._property_setter

    @property
    def property_getter(self, is_it: bool) -> None:
        if is_it:
            property_getter = True
            property_setter = False
        if self.property_refers_to is None:
            MemberFunctionOpt.__property_warning__()
        return

    @property_getter.getter
    def property_getter(self) -> bool:
        return self._property_getter


class EnumOpt(PybindOpt):
    
    def __init__(self, expose: bool = True,
                make_arithmetic: bool = False):

        PybindOpt.__init__(self, expose)
        self.make_arithmetic = make_aritmetic
        return


class ClassOpt(PybindOpt):

    def __init__(self, expose: bool = True,
                py_inheritable: bool = False,
                py_inheritable_base: bool = False,
                py_extendabl: bool = False,
                pybind_class_obj = "py::class_",
                limit_py_inherited_to: typing.List[str]: [],
                module_local: bool = False,
                is_final: bool = False,
                friendly: bool = False):

        PybindOpt.__init__(self, expose)
        self.py_inheritable = py_inheritable
        self.py_inheritable_base = py_inheritable_base
        self.py_extendable = py_extendable
        self.pybind_class_obj = pybind_class_obj
        self.limit_py_inherited_to = limit_py_inherited_to
        self.module_local = module_local
        self.is_final = is_final
        self.friendly = friendly
        return

class ClassTemplateOpt(PybindOpt):

    def __init__(self, expose: bool = True):
        PybindOpt.__init__(self, expose)
        return

class FunctionTemplateOpt(PybindOpt):

    def __init__(self, expose: bool = True):
        PybindOpt.__init__(self, expose)
        return


class UnionOpt(PybindOpt):

    def __init__(self, expose: bool = True):
        PybindOpt.__init__(self, expose)
        return


pybind_opt_map = {
        EnumObject: EnumOpt,
        EnumConstDeclObject: PybindOpt,
        ClassObject: ClassOpt,
        FunctionObject: FunctionOpt,
        MemberFunctionObject: MemberFunctionOpt
        FunctionParamObject: FunctionParamOpt,
        MemberVariableObject: MemberVariableOpt,
        VariableObject: VariableOpt,
        TypeDefObject: PybindOpt,
        TypeAliasObject: PybindOpt,
        NamespaceAliasObject: PybindOpt,
        TemplateAliasObject: PybindOpt,
        UsingNamespaceObject: PybindOpt,
        UsingDeclarationObject: PybindOpt,
        TemplateObject: PybindOpt,
        UnionObject: UnionOpt,
        TemplateParamObject: PybindOpt
        }
        
