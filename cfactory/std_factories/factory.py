import os
import sys
from typing import *
from functools import wraps
from datetime import datetime
import re

import illuminate.__config__.illuminate_config as il_cfg
import illuminate.collections.illuminate_package as pkg
from illuminate.code_models.namespace import NamespaceObject
from illuminate.code_models.template import TemplateObject
import illuminate.utils.file_sys as fs

var_pattern = re.compile("(?P<var>^[a-zA-Z_][a-zA-Z0-9_]*)")

namespace_to_module = {}
module_to_namespace = {}

factory_registered_types = []
factory_registered_writers = {}

class FactoryType(object):
    BINDING = 0
    EXTENSION = 1
    META = 2

def machine_writer(method):

    @wraps(method)
    def _add_machine_writer(obj: 'Machine', method):
        if self.module not in factory_registered_writers:
            factory_registered_writers[self.module] = []
        if method not in factory_registered_writers[self.module]:
            factory_registered_writers[self.module].append(method)
        return 

    return _add_machine_writer


def expand_template_name(t_obj: TemplateObject) -> str:
    append_arr = []
    for tval, tparam in zip(t_obj.parameter_values, t_obj.template_parameters):
        if tparam.is_type_param or tparam.is_non_type_param:
            append_arr.append(str(tval))
        elif tparam.is_template_template_param:
            append_arr.append(expand_template_name(tval))
    return "_".join([t_obj.get_name(), *append_arr])

class ParseObjectWrapper(object):

    def __init__(self, parse_object: 'ParseObject', pkg_name: str):
        self.parse_object = parse_object
        self.header_file = parse_object.header.header_file
        self.pkg_name = pkg_name
        self.module_name = self.pkg_name + \
                ">" + ">".join(self.parse_object.qualified_id.split("::")[:-1])

        self.name = None
        if var_pattern.match(self.parse_object.get_name()).groups("var") == \
                self.parse_object.get_name():
            self.name = self.parse_object.get_name()
        elif isinstance(parse_object, TemplateObject):
            if parse_object.is_variadic:
                raise RuntimeError('Variadic template has no compatible name specified')
            exname = expand_template_name(parse_object)
            self.name = exname if ParseObjectWrapper.valid_pyname else None

        return

    def get_pypackage(self) -> str:
        return self.pkg_name.replace('>', '.')

    def get_pymodule(self) -> str:
        module = self.parse_object.qualified_id.split('::')[:-1]
        return self.get_pypackage() + module.replace('::', '.')

    @staticmethod
    def valid_pyname(name_in) -> bool:
        if name_in is None:
            return False
        return var_pattern.match(name_in).group("var") == \
                name_in

    def get_jspackage(self) -> str:
        pass

    def get_jsmodule(self) -> str:
        pass

    @staticmethod
    def valid_jsname(self) -> str:
        pass

    def get_cpackage(self) -> str:
        return self.pkg_name.replace('>', os.sep)

    def get_cscope(self) -> str:
        if self.parse_object.scope is None:
            return ""
        return self.parse_object.scope.qualified_id

    def get_cid(self) -> str:
        return self.parse_object.qualified_id

    def get_header(self) -> str:
        return self.parse_object.header.header_file


class Factory(object):

    headers = {}
    module_parents = {}
    factory_registered_types = []
    wrapped_objects = {}

    def header_dict() -> Dict:
        new_dict = {
                "package_dir": "",
                "modules": [],
                "package_name": "",
                "header_name": "",
                "internal_dependencies": set(),
                "external_dependencies": set(),
                "description": "",
                "objects": []
                }
        return new_dict

    def process_headers(self, summary: 'UnitSummary') -> None:
       
        if summary.ref in Factory.headers:
            return

        modules = {}
        for ns in summary.namespaces:
            if ns.get_name() == "GlobalNamespace":
                modules[self.pkg_name] = (self.pkg_name, None)
            else:
                mod_name = self.pkg_name + ">" + \
                        ns.qualified_id.replace("::", ">")
                p_name = self.pkg_name if ns.scope.get_name() == "GlobalNamespace" \
                        else self.pkg_name + ">" + ns.scope.qualified_id.replace("::", ">")
                modules[self.pkg_name] = (mod_name, p_name)

        header_dict = Factory.header_dict()
        header_dict["package_dir"] = self.package.illuminate_pkg_abspath
        header_dict["modules"] = modules
        header_dict["package_name"] = self.package.illuminate_pkg_name
        header_dict["header_name"] = summary.ref
        header_dict["description"] = summary.long_desc
        header_dict["objects"] = [ParseObjectWrapper(x, self.package.illuminate_pkg_name) for 
                x in summary.all_objects]

        for m, v in modules.items():
            Factory.module_parents[m] = v

        for obj in header_dict["objects"]:
            wrapped_objects[obj.parse_object.qualified_id] = obj
            header_dict["internal_dependencies"].union({*summary.unit_headers})
            header_dict["external_dependencies"].union({*summary.extern_headers})

        return

    def check_out_dir(self) -> None:
        if not os.path.isdir(self.out_dir):
            os.mkdir(self.out_dir)
        with fs.cd(self.out_dir) as cwd:
            for dfile in os.listdir():
                if dfile.startswith(file_prefix):
                    os.remove(dfile)
        return
        
    def machine_writer(writer_dict):
        def _machine_writer(method):
            @wraps(method)
            def _add_machine_writer(self: 'Machine', *args, **kwargs):
                if self.module not in writer_dict:
                    writer_dict[self.module] = set()
                writer_dict[self.module].union({method})
                return
            return _add_machine_writer
        return _machine_writer

    def __init__(self, package: 'IlluminatePackage', out_dir: str = "", file_prefix: str = ""):
        self.package = package
        self._registered_types = []
        self._machine_auto_writers = []
        self.process_all_modules()
        self.out_dir = out_dir
        self.pkg_name = self.package.illuminate_pkg_name
        self.file_prefix = file_prefix

        license_file = open(il_cfg.license_file, 'r')
        self.license_text = license_file.read()
        license_file.close()

        self.header = self.write_illuminate_header()

        return

    def process_all_modules(self) -> None:
        self.check_out_dir()
        for summary in self.package.summary.header_summaries:
            self.process_headers(summary)
        return

    def write_illuminate_header(self, file_name: str) -> None:
        self.header = f"""/*******************************************************************************
        This file has been autogenerated by illuminate. It is not advised that this file 
        be modified directly-- rather, new machines and/or rules should be written to 
        customize the contents of this file.

        Name: {file_name}
        Created: {str(datetime.utcnow())}
        ********************************************************************************/
        """
        return
