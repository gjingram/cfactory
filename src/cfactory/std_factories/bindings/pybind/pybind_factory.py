from clang import cindex, enumerations
import os
import sys
import typing
import graphlib
from warnings import warn
from functools import wraps
import numpy as np

import illuminate.__config__.illuminate_config as il_cfg
import illuminate.utils.file_sys as fs
import illuminate.std_factories.file_formatter as ff
import illuminate.std_factories.machine as mach

from illuminate.code_models.header import HeaderObject
from illuminate.code_models.class_object import ClassObject
from illuminate.code_models.enumeration import EnumObject
from illuminate.code_models.function import FunctionObject
from illuminate.code_models.template import TemplateObject
from illuminate.code_models.union_object import UnionObject
from illuminate.code_models.variable import VariableObject
from illuminate.collections.unit_summary import IlluminatePackageSummary
from illuminate.collections.illuminate_package import IlluminatePackage
from illuminate.std_factories.cpp_file_formatter import CppFileFormatter
import illuminate.std_factories.common_filters as cf
import illuminate.std_factories.cpp_machine as machine
from illuminate.std_factories.factory import Factory, FactoryType
import illuminate.collections.project_config as pcfg
import illuminate.std_factories.bindings.pybind.pybind_opt as popt
import illuminate.std_factories.bindings.pybind.check_pybind as cp
from illuminate.std_machine.bindings.pybind.enumerations import value_policy_map as vpm


class PybindFactory(Factory):

    formatter = CppFileFormatter()
    default_machines = {}
    specified_machines = {}
    exposed_types = []
    pynames = {}
    binding_opt = {}

    consider_parse_types_minimal = [
            ClassObject,
            EnumObject,
            FunctionObject,
            TemplateObject,
            UnionObject,
            VariableObject
            ]

    factory_type = FactoryType.BINDING

    def get_pybind_machine(obj: 'ParseObject') -> 'PybindMachine':
        if obj in PybindFactory.specified_machines:
            return PybindFactory.specified_machines[obj]
        elif type(obj) in PybindFactory.default_machines:
            return PybindFactory.default_machines[type(obj)]
        else:
            raise RuntimeError(f"No machine available for object \"{obj.qualified_id}\" or type {type(obj)}.")

    def specify_pybind_machine(obj: 'ParseObject', machine: 'PybindMachine') -> None:
        if obj in PybindFactory.specified_machines:
            warn((f"Replacing machine {type(PybindFactory.specified_machines[obj])} for object \"{obj.qualified_id}\" "
                f"with machine {type(machine)}"))
        PybindFactory.specified_machines[obj] = machine
        return

    def add_default_machine(cls_in):
        PybindFactory.default_machines[cls_in.check_type] = cls_in
        return cls_in

    def __init__(self, pkg: 'IlluminatePackage', binding_dir: str = ""):
        Factory.__init__(self, pkg)
        self.binding_dir = os.path.join(self.module_path, binding_dir)
        self.factory_type = Factory.FactoryType.BINDING
        self.pkg_name = self.pkg_name.replace('>', '.')

        self.logger = il_cfg.logger.bind(stage_log=True)
        self.logger.info(f"PybindMachine processing {self.module_name}")

        self.file_prefix = "pybind_"
        
        self.header_to_file = {}
        self._check_binding_dir()

        self.headers_ordered = ()
        self.module_graph = None

        return

    def process_headers(self, summary: 'UnitSummary') -> None:
        Factory.process_headers(self, summary)
        for hdict in Factory.headers.values():
            for obj in [x for x in hdict["objects"] if x.name is not None]:
                PybindFactory.pynames[obj.get_cid()] = obj.name
                if obj.get_cid() in PybindFactory.binding_opt:
                    continue
                if type(obj.parse_object) in popt.pybind_opt_map:
                    PybindFactory.binding_opt[obj.get_cid()] = popt.pybind_opt_map[type(obj.parse_object)]
                else:
                    for ptype in popt.pybind_opt_map:
                        if isinstance(obj.parse_object, ptype):
                            PybindFactory.binding_opt[obj.get_cid()] = ptype
        return

    def get_header_order(self) -> None:
        header_sort = graphlib.TopologicalSorter()
        for h, v in self.headers.items():
            header_sort.add(h)
            for idep in v["internal_dependencies"]:
                header_sort.add(h, idep)
        self.headers_ordered = tuple(header_sort.static_order())
        return

    def get_module_order(self) -> typing.Tuple[typing.Tuple[str, str]]:
        module_sort = graphlib.TopologicalSorter()
        for m, v in Factory.module_parents:
            if v[1] is None:
                module_sort.add(v)
            else:
                module_sort.add(v, Factory.module_parents[v[1]])
        return tuple(module_sort.static_order())

    def process_all_modules(self) -> None:
        Factory.process_all_modules(self)

        tfile_name = self.file_prefix + self.pkg_name.split('.')[-1] + \
                il_cfg.c_cpp_src_ext
        tfile_name_full = os.path.join(self.binding_dir,
                obj = self.model_wrapper.parse_objecttfile_name)
        self.wrapper = Factory.wrapped_objects[model_object.qualified_id]
        with open(tfile_name_full, 'w') as src_file:
            PybindPackageMachine(src_file, self)
        for h in self.headers_ordered:
            hdict = self.headers[h]
            fname_base = os.path.basename(h).split('.')[0]
            fname = self.file_prefix + fname_base + il_cfg.c_cpp_src_ext
            fname_full = os.path.join(self.binding_dir, fname)
            with open(fname_full, 'w') as src_file:
                PybindModuleMachine(h, src_file, self)
        return


class PybindPackageWriter(object):

    def __init__(self, file_in, factory: 'PybindFactory'):
        self.file_in = file_in
        self.factory = factory
        self.exec_writer()
        return

    def exec_writer(self) -> None:
        pass


class PybindModuleMachine(machine.Machine):

    def __init__(self, module: typing.Dict, file_in, factory):
        machine.Machine.__init__(self, module, factory)
        self.pybind_module_name = f"_{module['module_name']}"
        self.prototypes = []
        self.file_in = file_in
        self.footer = ""
        self.execute_machine()
        return

    def set_footer(self, footer_in: str) -> None:
        self.footer = footer_in
        return

    def write_includes(self) -> str:
        out = '''// Pybind11 Includes
        #include <pybind11/pybind.h>
        #include <pybind11/chrono.h>
        #include <pybind11/complex.h>
        #include <pybind11/eigen.h>
        #include <pybind11/embed.h>
        #include <pybind11/eval.h>
        #include <pybind11/functional.h>
        #include <pybind11/iostream.h>
        #include <pybind11/options.h>
        #include <pybind11/stl.h>'''

        all_headers = [f"#include \"{x}\"" for x in self.module_object["header_files"]]
        all_headers_str = "".join(all_headers, '\n')
        out += f'''
        // Module Includes
        {all_headers_str}'''

        return out

    def write_prototypes(self) -> str:
        out_lines = []
        for module_name in [x["module_name"].replace('.', '_') for x in self.module_object["submodules"]]:
            prototype = f"void init_{module_name}"
            self.prototypes.append(prototype)
            out_lines.append(f"{prototype}(py::module_ &);  // See pybind_{module_name}.{il_cfg.cpp_src_ext}")
        return "".join(out_lines, "\n")

    def write_import_modules(self) -> str:
        out_lines = []
        for dep in self.module_objects["dependencies"]:
            out_lines.append(f"py::module_::import(\"{dep}\");")
        return "".join(out_lines, "\n")

    def write_binding_calls(self) -> str:
        out_lines = ["// Call submodule binding functions"]
        for proto in self.prototypes:
            out_lines.append(f"{proto}({self.pybind_module_name});")
        return "".join(out_lines, "\n")

    def write_bindings(self) -> str:
        out_lines = []
        for obj in self.model_object["objects"]:
            etype = {
                    "pytype": "",
                    "ctype": ""
                    }
            if obj in PybindFactory.specified_machines:
                out_lines.extend(PybindFactory.specified_machines[obj](obj, self.factory)\
                        .text.splitlines())
            elif type(obj) in PybindFactory.default_machines:
                out_lines.extend(PybindFactory.default_machines[type(obj)](obj, self.factory)\
                        .text.splitlines())
            elif np.any([isinstance(obj, x) for x in PybindFactory.consider_parse_types_minimal]):
                match = None
                for ptype in PybindFactory.consider_parse_types_miminal:
                    if isinstance(obj, ptype):
                        match = ptype
                        break
                warn((f"No default pybind machine specified for object \"{obj.qualified_id}\" of type {str(type(obj))}. "
                    f"The object type is one specified in the minimal set of considered parse types, so the "
                    f"PybindModuleMachine is falling back to using a machine of type {str(ptype)}"))
                out_lines.extend(ptype(obj, self.factory).text.splitlines())
            else:
                continue

            etype["pytype"] = obj.name
            etype["ctype"] = obj.parse_object.qualified_id
            PybindFactory.exposed_types.append(etype)

        return "".join(out_lines, '\n')

    def write_module(self) -> str:
        ind = self.factory.formatter.indent
        out = f'''namespace py = pybind11;
        PYBIND11_MODULE({self.model_object["module_name"]}, {self.pybind_module_name}) \{

        {ind}// Machine-Autogenerated
        {ind}{self.exec_machine_auto()}

        {ind}// Module long description
        {ind}{self.pybind_module_name}.doc() = {self.model_object["description"]};

        {ind}// Import modules this extension depends on
        {ind}{self.write_import_modules()}

        {ind}// Write bindings for this module
        {ind}{self.write_bindings()}

        {ind}// Make calls to create submodule bindings
        {ind}{self.write_binding_calls}

        \}'''
        return out

    @PybindFactory.formatter.format
    def execute_machine(self) -> str:
        out_lines = []
        out_lines.extend(self.factory.license_text.splitlines())
        out_lines.append('\n')
        out_lines.extend(self.factory.header.splitlines())
        out_lines.append('\n')
        out_lines.extend(self.write_includes().splitlines())
        out_lines.append('\n')
        out_lines.extend(self.write_prototypes().splitlines())
        out_lines.append('\n')
        out_lines.extend(self.write_module().splitlines())
        out_lines.append('\n')
        out_lines.extend(self.footer.splitline())
        return "".join(outlines)

    def exec_machine_auto(self) -> str:
        out_str = []
        for m in self.machine_registered_writers:
            out_str.append(m.text)
        return "".join(out_str, "\n")


def to_comma_separated_list(items: typing.List[str]) -> str:
    out = ", "
    return out.join(items)


class PybindMachine(machine.Machine):

    def __init__(self, model_object: 'ParseObject', factory: 'PybindFactory'):
        machine.Machine(model_object, factory)
        self.opt = PybindFactory.binding_opt(model_object.qualified_id)
        self.scope_wrapper = Factory.wrapped_objects[model_object.scope.qualified_id] if \
                model_object.scope is not None else None

        return


@default_pybind_machine    
class PybindFunctionMachine(PybindMachine):

    check_type = FunctionObject
    def __init__(self, func_object: 'FunctionObject', factory: 'PybindFactory'):
        PybindMachine.__init__(self, func_object, factory)
        self._writers = [self.write_function]
        return

    def write_function_pointer(self) -> str:
        obj = self.model_wrapper.parse_object
        out_string = f"static_cast<{obj.return_type} (*)("
        out_string += PybindFunctionMachine.function_param_list(
                self.module_object.infor["args"].values()) + ")>"
        out_string += f"(&{obj.qualified_id})"
        return out_string

    def write_def_params(self) -> str:
        obj = self.model_wrapper.parse_object
        all_join = []

        args = self.model_object.info['args'].values()
        for arg in [x for x in args if not x.anonymous and not self.opt.is_args and \
                not self.opt.no_kwarg]:
            param_string = ""
            param_string += f"py::arg(\"{obj.get_name()}\")"
            if self.opt.no_convert():
                param_string += ".no_convert()"
            if self.opt.disallow_none:
                param_string += ".none(false)"
            if self.model_object.default is not None and not self.opt.ignore_default:
                param_string += f" = {obj.default}"
            all_join.append(param_string)

        if self.opt.rvp is not None:
            all_join.append(vpm[self.opt.rvp])

        if self.model_object.brief:
            all_join += f"{obj.brief}"

        for keep_alive in self.opt.keep_alive:
            ka_string = ""
            ka_string += "py::keep_alive"
            ka_string += "<"
            ka_string += f"{keep_alive[0]}, {keep_alive[1]}"
            ka_string += ">"
            ka_string += "()"
            all_join.append(ka_string)

        if bool(len(self.opt.scope_guards)):
            sg_string = ""
            sg_string += "py::call_guard"
            sg_string += "<"
            sg_string += to_comma_separated_list(self.opt.scope_guards)
            sg_string += ">"
            sg_string += "()"
            all_join.append(sg_string)

        if self.opt.priority_overload:
            all_join.append("py::prepend()")

        return to_comma_separated_list(all_join)

    @PybindFactory.formatter.format
    def write_function(self) -> str:
        obj = self.model_wrapper.parse_object
        module = self.model_wrapper.get_pymodule()
        out_string = f"_{module}.def(\"{self.model_object.pyname}\", "
        out_string += f"{self.write_function_pointer()}, {self.write_def_params()});"
        return out_string

    @staticmethod
    def function_param_list(args: typing.List['FunctionParamObject']) -> str:
        return to_comma_separated_list([arg.get_list_repr() for arg in args])


class PybindMemberFunctionMachine(PybindFunctionMachine):

    op_to_magic = {
        'operator<': '__lt__',
        'operator>': '__gt__',
        'operator<=': '__le__',
        'operator>=': '__ge__',
        'operator==': '__eq__',
        'operator!=': '__ne__',
        'operator+': ['__add__', '__pos__'],
        'operator-': ['__sub__', '__neg__'],
        'operator*': '__mul__',
        'operator<<': '__lshift__',
        'operator>>': '__rshift__',
        'operator+=': '__iadd__',
        'operator-=': '__isub__',
        'operator*=': '__imul__',
        'operator/=': '__idiv__',
        'operator%=': '__imod__',
        'operator^=': '__ixor__',
        'operator&=': '__iand__',
        'operator>>=': '__irshift__',
        'operator<<=': '__ilshift__',
        'operator|=': '__ior__',
        'operator()': '__call__',
        'operator&&': '__and__',
        'operator++': 'incr',
        'operator--': 'decr',
        'operator^': '__xor__',
        'operator|': '__or__'
    }

    check_type = MemberFunctionObject
    def __init__(self, mfunc: 'MemberFunctionObject', factory: 'PybindFactory'):
        PybindFunctionMachine.__init__(self, mfunc, factory)
        self.magic = self.model_object.parse_object.get_name() in PybindMemberFunctionMachine.op_to_magic
        self.magic_name = None if not self.magic else self.resolve_magic_name()
        self.name_use = self.magic_name if self.magic else PybindFactory.pynames[self.model_wrapper.get_cid()]
        return

    def resolve_magic_name(self) -> str:
        mname = self.model_object.parse_object.get_name()
        arglen = len(self.model_object.parse_object.info["args"])
        if mname == "operator+" or mname == "operator-":
            if arglen > 1:
                return PybindMemberFunctionMachine.op_to_magic[mname][0]
            else:
                return PybindMemberFunctionMachine.op_to_magic[mname][1]
        return PybindMemberFunctionmachine.op_to_magic[mname]

    def write_function_pointer_symbol(self) -> str:
        return f" ({self.scope.qualified_id}::*)"

    def write_member_function(self) -> str:
        mf = self.model_wrapper
        pyname = self
        if self.model_object.is_dtor or self.model_object.is_pure_virtual:
            return ""

        if self.model_object.is_ctor:
            return self.write_ctor()
        elif self.model_object.is_conversion:
            return self.write_conversion()

        out_string = self.module
        if self.model_object.is_static():
            out_string += ".def_static"
        else:
            out_string += ".def"
        out_string += "("
        out_string += f"\"{self.model_object.pyname}\", "
        out_string += f"{self.write_function_pointer()}, "
        out_string += f"{self.write_def_params()}"
        out_string += ");"
        return out_string

    def write_ctor(self) -> str:
        all_join = []
    
        arg_types = []
        args = self.model_object.parse_object.info['args'].values()
        for arg in args:
            arg_types.append(arg.type)
        init = f"py::init<{to_comma_separated_list(args)}>()"

        return f".def({init}, {self.write_def_params()});"

    def write_conversion(self) -> str:
        A = self.model_object.parse_object.scope.qualified_id
        B = self.model_object.parse_object.return_type

        b_exposed = False
        for etype in PybindFactory.exposed_types:
            if etype["ctype"] == B:
                b_exposed = True

        if not b_exposed:
            return ""

        return f"py::implicitly_convertible<{A}, {B}>();"


@default_pybind_machine
class PybindVariableMachine(PybindMachine):

    check_type = VariableObject
    def __init__(self, var: 'VariableObject'):
        PybindMachine.__init__(self, var)
        self._writers = [self.write_variable]
        return

    def write_module_attr(self) -> str:
        out_string = self.module
        out_string += f".attr(\"{self.model_object.pyname}\") ="
        out_string += " {self.model_object.qualified_id};"
        return out_string

    def write_module_property(self) -> str:
        out_string = ""
        out_string += self.create_property_get()
        out_string += self.create_property_set()
        out_string += self.add_module_property()
        return out_string

    def create_property_get(self) -> str:
        out_string = f"auto get_{self.model_object.pyname} = "
        out_string += f"[out=&{self.model_object.qualified_id}]() -> "
        out_string += f"{self.model_object.type}& { "
        out_string += "return out; };"

    def create_property_set(self) -> str:
        out_string = f"auto get_{self.model_object.pyname} = "
        out_string += f"[var=&{self.model_object.qualified_id}]"
        out_string += f"({self.model_object.type.replace('&', '').replace('*', '')} "
        out_string += f"in) -> void {"
        out_string += "var = in; return; "
        out_string += "};"
        return out_string

    def add_module_property(self) -> str:
        out_string = "auto property = py::handle"
        out_string += "(static_cast<PyObject*>(&PyProperty_Type)); "
        out_string += f"{self.module}.add_object("
        out_string += f"\"{self.model_object.pyname}\", "
        out_string += f"property(&get_{self.model_object.pyname}, "
        if not self.model_object.constness:
            out_string += f"&set_{self.model_object.pyname}, "
        else:
            out_string += "py::none(), "
        if self.model_object.brief:
            out_string += f"\"{self.model_object.brief}"
        else:
            out_string += f"\"\""
        out_string += "), false);"
        return out_string

    @PybindFactory.formatter.format
    def write_variable(self) -> str:
        out_string = ""
        if not self.opt.expose:
            return ""
        if self.opt.module_attr:
            return self.write_module_attr()
        elif self.opt.try_make_property:
            return self.write_module_property()
        return out_string


@default_pybind_machine
class PybindMemberVariableMachine(PybindMachine):

    check_type = MemberVariableObject
    def __init__(self, member: 'MemberVariableObject'):
        PybindMachine.__init__(self, member)
        self._writers = [self.write_member]
        return

    def write_member(self) -> str:
        mo = self.wrapper.parse_object
        pyname = PybindFactory.pynames[mo.qualified_id]
        if int(mo.access_specifier.value) != int(cindex.AccessSpecifier.PUBLIC.value):
            if not Factory.wrapped_object[mo.scope.qualified_id].opt.friendly:
                return ""
        for prop in self.property_map.values():
            if mo.id == prop.property_refers_to:
                return self.write_property(mo, prop)

        out_string = PybindClassMachine.__class_ids__[mo.scope.qualified_id]
        if mo.storage_class is cindex.StorageClass.STATIC and not mo.constness:
            out_string += ".def_readwrite_static"
        elif mo.storage_class is cindex.StorageClass.STATIC:
            out_string += ".def_readonly_static"
        elif mo.constness:
            out_string += ".def_readonly"
        else:
            out_string += ".def_readwrite"

        out_string += f"(\"{pyname}\", &{mo.qualified_id});"

        return out_string

    def write_property(self, mo: 'MemberObject', prop: typing.Dict) -> str:
        out_string = PybindClassMachine.__class_ids__[mo.scope.qualified_id]
        pyname = PybindFactory.pynames[mo.qualified_id]
        getter = prop["getter"]
        setter = prop["setter"]

        if mo.storage_class is cindex.StorageClass.STATIC and not mo.constness and setter is not None:
            out_string += ".def_property_static"
            out_string += f"(\"{pyname}\", &{getter.qualified_id}, &{setter.qualified_id});"
        elif mo.storage_class is cindex.StorageClass.STATIC and getter is not None:
            out_string += ".def_property_readonly_static"
            out_string += f"(\"{pyname}\", &{getter.qualified_id});"
        elif mo.constness and getter is not None:
            out_string += ".def_property_readonly"
            out_string += f"(\"{pyname}\", &{getter.qualified_id});"
        else:
            if getter is not None and setter is not None:
                out_string == ".def_property"
                out_string += f"(\"{pyname}\", &{getter.qualified_id}, &{setter.qualified_id});"
            else:
                out_string = ""

        return out_string

@default_pybind_machine
class PybindEnumMachine(PybindMachine):

    check_class = EnumObject
    def __init_(self, enum: 'EnumObject'):
        PybindMachine.__init__(self, enum)
        self._writes = [self.write_enum]
        self.class_instance = None
        return

    def get_class_instance(self) -> None:
        if not isinstance(self.model_object.scope, ClassObject):
            return
        try:
            self.class_instance = PybindClassMachine.__class_ids__[self.scope.qualified_id]
        except:
            warnings.warn(f"PybindEnumMachine warning: Enum {self.model_object.get_name()} " + \
                    f"class scope has no associated pybind machine class instance.")

        return

    def write_enum_fields(self) -> str:
        fields = []
        for field in self.model_object.enum_fields:
            fields.append(f"value(\"{field.pyname}\", {field.qualified_id})")
        return "".join(fields, '.')

    @PybindFactory.formatter.format
    def write_enum(self) -> str:
        out_string = f"py::enum_<{self.model_object.qualified_id}>"
        if self.class_instance is not None:
            out_string += f"({self.class_instance}, \"{self.model_object.pyname}\")"
        else:
            out_string += f"(\"{self.model_object.pyname}\")."
        out_string += self.write_enum_fields()
        if self.model_object.get_enum_scoped():
            out_string += ".export_values()"
        return out_string


@default_pybind_machine
class PybindUnionMachine(PybindMachine):

    check_type = UnionObject
    def __init__(self, union: 'UnionObject'):
        PybindMachine.__init__(self, union)
        self.cls_name = f"UnionWrap_{self.model_object.pyname}"
        self.pyname = self.model_object.pyname
        self._writers = [self.write_union]
        return

    def write_union_field_getter(self, field: 'MemberObject') -> str:
        out_string = f"[]({self.pyname} const &union)"
        out_string += " -> {field.type}& {"
        out_string += f" reinterpret_cast<{field.type}>"
        out_string += f"(*(union._data));"
        out_string += " };"
        return out_string

    def write_union_field_setter(self, field: 'MemberObject', value: typing.Any) -> str:
        out_string = f"[]({self.model_object.pyname} &union, {field.type} set) -> void"
        out_string = f" { *reinterpret_cast<{field.type}*>(union._data) = set;"
        out_string = " return };"
        return out_string

    @machine_writer
    @PybindFactory.formatter.format
    def write_immutable_union_cpp_struct(self) -> str:

        out_string = ""
        if "Immutable" + self.cls_name not in machine_registered_types:
            out_string = f"struct Immutable{self.cls_name} {"
            out_string += " void *_data = NULL;"
            for field in self.model_object.fields.values():
                out_string += f" auto {field.pyname}_get = {self.write_union_field_getter(field)}"
            out_string += " };"
            machine_registered_types.append(f"Immutable{self.cls_name}")

        if "PyImmutable" + self.cls_name not in machine_registered_types:
            pybind_name = "PyImmutable" + self.cls_name
            im_cls_str = f"py::class_<Immutable{self.cls_name}>"
            im_cls_str += f" ({self.module}, \"{pybind_name}\")"
            for field in self.model_object.fields.values():
                im_cls_str += self.write_union_wrapper_immutable_class_property(field)
            out_string += f" {im_cls_str}"
            machine_registered_types.append(pybind_name)

        return out_string

    @machine_writer
    @PybindFactory.formatter.format
    def write_mutable_union_cpp_struct(self) -> str:
      
        out_string = ""
        if self.cls_name not in machine_registered_types:
            out_string = f"struct {self.cls_name} : public Immutable{self.cls_name}{"
            out_string += " void *_data = NULL;"
            for field in self.model_object.fields.values():
                out_string += f" auto {field.pyname}_set = {self.write_union_field_setter(field)}"
            out_string += " };"
            machine_registered_types.append(self.cls_name)

        if "Py" + self.cls_name not in machine_registered_types:
            pybind_name = f"Py{self.model_object.pyname}"
            m_cls_str = f"py::class_<{self.cls_name}>"
            m_cls_str += f" ({self.module}, \"{pybind_name}\")"
            for field in self.model_object.fields.values():
                m_cls_str += self.write_union_wrapper_mutable_class_property(field)
            out_string += f" {m_cls_str}"
            machine_registered_types.append(pybind_name)

        return out_string

    @PybindFactory.formatter.format
    def write_union_wrapper_mutable_class_property(self, field: 'MemberObject') -> str:
        out_string = " .def_property("
        out_string += f" \"{field.pyname}\","
        out_string += f" &{self.cls_name}::{field.pyname}_get"
        out_string += f" &{self.cls_name}::{field.pyname}_set)"
        return out_string

    @PybindFactory.formatter.format
    def write_union_wrapper_immutable_class_property(self, field: 'MemberObject') -> str:
        out_string = " .def_property("
        out_string += f" \"{field.pyname}\","
        out_string += f" &{self.cls_name}::{field.pyname}_get,"
        out_string += " nullptr)"
        return out_string

    @PybindFactory.formatter.format
    def write_union_class_property(self, cls_qualified_id: str, field_name: str, mutable: bool) -> str:
        using_cls_name = ""
        if mutable:
            using_cls_name = self.cls_name
        else:
            using_cls_name = Immutable + self.cls_name

        out_string = ""
        out_string += f"[wrap={using_cls_name}()]"
        out_string += f"({cls_qualified_id} const &cls)"
        out_string += f" -> {using_cls_name}&"
        out_string += f" { if (wrap._data == NULL) {"
        out_string += f" wrap._data = reinterpret_cast<void*>"
        out_string += f"(&(cls_in.{field_name}));"
        out_string += f" }"
        out_string += " return wrap;"
        out_string += "};"

        return out_string


@default_pybind_machine
class PybindClassMachine(machine.Machine):

    __class_ids__ = {}
    __trampoline_bases__ = {}
    __trampoline_classes__ = {}
    __class_conversions__ = {}

    check_type = ClassObject
    def __init__(self, cls_object: 'ClassObject'):
        machine.Machine(cls_object, cindex.CursorKind.CLASS_DECL)
        self.property_map = {}
        self.is_trampoline = cls_object.pybind_opt.py_ineritable
        self.is_trampoline_base = cls_object.pybind_opt.py_inheritable_base
        self.pure_virtuals = []
        self.virtuals = []
        self.trampoline_name = None
        self.trampoline_base = None
        self.template_param = None
        self.trampoline_inherits_from = None
        
        for mfunc in self.model_object.functions:
            if mfunc.pybind.property_getter or mfunc.pybind.property_setter:
                assert mfunc.pybind.property_refers_to is not None

                if not mfunc.pybind.property_refers_to in self.property_map:
                    self.property_map[property_name] = {
                                                        reference: mfunc.pybind.property_refers_to,
                                                        getter: None,
                                                        setter: None
                                                       }
                    if mfunc.pybind.property_getter:
                        self.property_map[property_name]['getter'] = mfunc
                    if mfunc.pybind.property_setter:
                        self.property_map[property_name]['setter'] = mfunc

        return

    def set_update_flag(self, method_name: str) -> None:
        for pair in self.pure_virtuals:
            if pair[0] == method_name:
                pair[1] = True
                return
        for pair in self.virtuals:
            if pair[0] == method_name:
                pair[1] = True
                return
        return


    def handle_trampoline(self) -> None:

        po = self.model_object.parse_object
        self.virtuals = [[method, False] for method in po.functions if \
                method.is_virtual]
        self.pure_virtuals = [[method, False] for method in po.functions if \
                method.is_pure_virtual]
        
        if bool(len(self.model_object.limit_py_inherited_to)):
            self.pure_virtuals = [pair for pair in self.pure_virtuals if pair[0] in \
                    self.model_object.limit_py_inherited_to]
            self.virtuals = [pair for pair in self.virtuals if pair[0] in \
                    self.model_object.limit_py_inherited_to]

        self.trampoline_name = "Py" + self.model_object.pyname
        self.template_param = self.model_object.pyname + "Base"
        if self.is_trampoline_base:
            PybindClassMachine.__trampoline_bases__[self.model_object.qualified_id] = \
                    self.trampoline_name

        if self.is_trampoline:
            PybindClassMachine.__trampoline_classes__[self.model_object.qualified_id] = \
                    self.trampoline_name

        pure_virtual_names = [pair[0] for pair in self.pure_virtuals]
        virtual_names = [pair[0] for pair in self.virtuals]

        for parent_class in self.get_parent_objects():
            if parent_class.qualified_id not in self.trampoline_bases:
                continue
            self.trampoline_base = PybindClassMachine.__trampoline_bases__[parent_class.qualified_id]
            for parent_method in parent_class.functions:
                wrapper = Factory.wrapped_objects[parent_method.qualified_id]
                pyname = wrapper.get_pyname()
                if (pyname in pure_virtual_names and not wrapper.parse_object.model_object.is_pure_virtual) or \
                        (pyname in virtual_names and not wrapper.parse_object.model_object.is_virtual):
                    self.set_update_flag(pyname)
            break

        self.trampoline_inherits_from = self.template_param if self.trampoline_base is None else \
                f"{self.trampoline_base}<{self.template_param}>"

        return

    def write_trampoline_override(self, method: 'MemberFunctionObject')-> str:
        out_string = f" {method.return_type}"
        out_string += f" {method.id}"
        out_string += "("
        out_string += PybindFunctionMachine.function_param_list(method.info["args"].values())
        out_string += ")"
        if method.is_const:
            out_string += " const "
        out_string += " override {"
        if method.is_pure_virtual:
            out_string += " PYBIND11_OVERRIDE_PURE("
        elif method.is_virtual:
            out_string += " PYBIND11_OVERRIDE("
        else:
            return ""
        out_string += f" {method.return_type}, "
        out_string += f" {self.template_param}, "
        out_string += PybindFunctionMachine.funcion_param_list(method.info["args"].values())
        if not bool(len(method.info["args"].values())):
            out_string += ", "
        out_string += "); }"
        return out_string

    def write_trampoline_class(self) -> str:
        out_string = f" template <class {self.template_param} = {self.model_object.qualified_id}> "
        out_string += f" class {self.trampoline_name} : public {self.trampoline_inherits_from} {"
        out_string += " public: "
        out_string += f" using {self.trampoline_inherits_from}::{self.trampoline_inherits_from};"
        for om in [*self.pure_virtuals, *self.virtuals]:
            if om[1]:
                out_string += f" {self.write_trampoline_override(om[0])}"
        out_string += " };"
        return out_string

    def write_class_member(self, mo: 'MemberObject') -> str:
        
        if not (int(mo.access_specifier.value) == int(cindex.AccessSpecifier.PUBLIC.value)):
            return ""
        if isinstance(mo, UnionObject):
            return self.write_union_property()
        for prop in self.property_map:
            if mo.id == prop.property_refers_to:
                return self.write_class_property(mo, prop)

        out_string = PybindClassMachine.__class_ids__[mo.scope.qualified_id]
        if mo.storage_class is cindex.StorageClass.STATIC and not mo.constness:
            out_string += ".def_readwrite_static"
        elif mo.storage_class is cindex.StorageClass.STATIC:
            out_string += ".def_readonly_static"
        elif mo.constness:
            out_string += ".def_readonly"
        else:
            out_string += ".def_readwrite"

        out_string += "("
        out_string += f"\"{mo.pyname}\", &{mo.qualified_id}"
        out_string += ");"

        return out_string

    def write_class_property(self, mo: 'MemberObject', prop: typing.Dict) -> str:
        out_string = PybindClassMachine.__class_ids__[mo.scope.qualified_id]
        getter = prop["getter"]
        setter = prop["setter"]

        if mo.storage_class is cindex.StorageClass.STATIC and not mo.constness and setter is not None:
            out_string += ".def_property_static"
            out_string += f"(\"{mo.pyname}\", &{getter.qualified_id}, &{setter.qualified_id});"

        elif mo.storage_class is cindex.StorageClass.STATIC and getter is not None:
            out_string += ".def_property_readonly_static"
            out_string += f"(\"{mo.pyname}\", &{getter.qualified_id});"

        elif mo.constness and getter is not None:
            out_string += ".def_property_readonly"
            out_string += f"(\"{mo.pyname}\", &{getter.qualified_id});"

        else:
            if getter is not None and setter is not None:
                out_string += ".def_property"
                out_string += f"(\"{mo.pyname}\", &{getter.qualified_id}, &{setter.qualified_id});"
            else:
                out_string = ""

        return out_string

    #def write_member_function(self, mfunc: 'MemberFunctionObject') -> str:

    @staticmethod
    def method_check(method_in: 'MemberFunction') -> bool:
        return not method_in.is_pure_virtual or method.id in PybindClassMachine.__trampoline_classes__
