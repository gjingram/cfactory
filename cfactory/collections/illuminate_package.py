import os
import sys
import pickle
import typing
import functools
import graphlib
import copy
import re
import pdb

import illuminate.parsers.cpp_parse as cppp
from illuminate.code_models.template import TemplateObject
from illuminate.collections.unit_summary import PackageSummary
import illuminate.utils.file_sys as fs
from illuminate.code_models.types import DependencyType
import illuminate.__config__.illuminate_config as il_cfg

from illuminate.code_models.class_object import ClassObject

def template_test(type_str: str) -> bool:
    return type_str.contains('<') and type_str.contains('>')

class BuildProtocol(object):
    COMPILE = 0
    COPY = 1
    PARSE = 2


class IlluminatePackage(object):

    def __init__(self, package_path:str, package_name: str="", source_ext: typing.List[str]=[],
            py_source_ext: typing.List[str]=[], header_ext: typing.List[str]=[],
            collection_ext: typing.List[str]=[],  project_name: str="",
            project_path: str=".", log_parse_objects: bool=False, log_object_dependencies: bool=False,
            log_module_dependencies: bool=False, license_file: str = ""):

        il_cfg.log_parsed = log_parse_objects
        il_cfg.log_object_deps = log_object_dependencies
        il_cfg.log_module_deps = log_module_dependencies
        
        if log_parse_objects or log_object_dependencies or log_module_dependencies:
            il_cfg.logger.enable("illuminate")

        
        self.project_name = package_name if project_name == "" else project_name
        self.project_path = package_path if project_path == "." else project_path
        self.illuminate_pkg_relpath = "." if project_path == "." else os.path.relpath(package_path, start=self.project_path)
        if package_name != "":
            self.illuminate_pkg_name = package_name
        else:
            self.illuminate_pkg_name = self.project_name + '>' + self.illuminate_pkg_relpath.replace(os.sep, '>') \
                    if self.illuminate_pkg_relpath != '>' else self.project_name
        self.illuminate_pkg_abspath = package_path

        il_cfg.project = self.project_name
        il_cfg.package = self.illuminate_pkg_name

        il_cfg.logger_registry[self.illuminate_pkg_name] = \
                il_cfg.logger.bind(log_parsed=il_cfg.log_parsed,
                log_object_deps=il_cfg.log_object_deps,
                log_module_deps=il_cfg.log_module_deps,
                project=self.project_name,
                package=self.illuminate_pkg_name)

        self.pkg_logger.bind(stage_log=True).info("Creating package {}".format(self.illuminate_pkg_name))

        self.current_scope = ""

        self.c_cpp_compiler_args = []

        self.source = []
        self.headers = []
        self.py_source = []
        self.collection_files = []

        self.inherits_c_cpp_compiler_args = True
        self.inherits_binding_factory = True
        self.inherits_extension_factories = True
        self.inherits_meta_factories = True

        self.binding_factory = None
        self.extension_factories = []
        self.meta_factories = []

        self.inherits_binding_dir = True
        self.inherits_extension_dir = True
        self.inherits_meta_dir = True
        self.inherits_factory_dir = True

        self.binding_dir = ""
        self.extension_dir = ""
        self.meta_dir = ""
        self.factory_out_dir = ""

        self.save_path = self.illuminate_pkg_abspath

        self.is_extension = False
        self.is_pypackage = False
        self.summary = IlluminatePackage.load_package_summary(
                self.illuminate_pkg_name, self.save_path, self.pkg_logger) 

        self.collect_all_files(py_source_ext, source_ext, header_ext, collection_ext)

        self.needs_recompile = False

        self.format_config = il_cfg.FormatterConfig()
        self.set_package_license_file(license_file)

        return

    def set_binding_directory(self, binding_dir: str) -> None:
        self.binding_dir = os.path.join(self.factory_out_dir, binding_dir)
        return

    def set_extension_directory(self, ext_dir: str) -> None:
        self.extension_dir = os.path.join(self.factory_out_dir, ext_dir)
        return

    def set_meta_directory(self, meta_dir: str) -> None:
        self.meta_dir = os.path.join(self.factory_out_dir, meta_dir)
        return

    def set_factory_directory(self, fact_dir: str) -> None:
        self.factory_out_dir = fact_dir
        self.binding_dir = os.path.join(fact_dir, self.binding_dir)
        self.extension_dir = os.path.join(fact_dir, self.extension_dir)
        self.meta_dir = os.path.join(fact_dir, self.meta_dir)
        return

    def using_namespace(self, ns: str) -> None:
        self.current_scope = ns
        return

    def using_global_namespace(self) -> None:
        self.current_scope = ""
        return

    @property
    def pkg_logger(self):
        return il_cfg.logger.bind(log_parsed=il_cfg.log_parsed,
                log_object_deps=il_cfg.log_object_deps,
                log_module_deps=il_cfg.log_module_deps,
                project=il_cfg.project,
                package=il_cfg.package)

    def process_package(self) -> None:
        files_to_update = self.get_files_to_update()
        for file_name, protocol in files_to_update:
            if protocol == BuildProtocol.COMPILE or protocol == BuildProtocol.PARSE:
                self.parse_and_update()
                self.needs_recompile = True
                return
        self._run_factories()
        return

    def add_factory(self, factory_cls) -> None:
        pdb.set_trace()
        if factory_cls is None:
            return
        if factory_cls.factory_type == factory.FactoryType.BINDING:
            self.binding_factory = factory_cls(self, os.path.join(self.illuminate_pkg_abspath,
                self.binding_dir))
        elif factory_in.factory_type == factory.FactoryType.EXTENSION:
            self.extension_factories.append(factory_cls(self, os.path.join(self.illuminate_pkg_abspath,
                self.extension_dir)))
        elif factory_in.factory_type == factory.FactoryType.META:
            self.meta_factories.append(factory_cls(self, os.path.join(self.illuminate_pkg_abspath,
                self.meta_dir)))
        return

    def parse_and_update(self, update_files=False) -> None:
        pdb.set_trace()

        if update_files:
            self.collect_all_files(self.py_source_ext, self.source_ext, self.header_ext, self.collection_ext)

        c_cpp_parser = cppp.ClangParseCpp(self.illuminate_pkg_abspath)
        c_cpp_parser.project_name = self.project_name
        c_cpp_parser.project_root_path = self.project_path
        c_cpp_parser.compiler_args = self.c_cpp_compiler_args
        c_cpp_parser.unit_name = self.illuminate_pkg_name
        c_cpp_parser.set_headers([os.path.join(self.illuminate_pkg_abspath, x[0]) for x in self.headers])
        c_cpp_parser.process_headers(self.pkg_logger)

        self.summary = PackageSummary(c_cpp_parser.unit_summaries)
        self.summary.ref = self.illuminate_pkg_name
        self.summary.py_source = self.py_source
        self.summary.source = self.source
        self.summary.internal_headers = self.headers
        self.summary.external_headers = c_cpp_parser.extern_includes
        self.summary.collection_files = self.collection_files

        self.summary.is_extension = bool(len(self.source))
        self.summary.is_package = bool(len(self.py_source)) and self.is_extension
        self.summary.is_pure_python_package = len(self.py_source) > 1 and not self.is_extension
        self.summary.is_namespace = not self.summary.is_extension and \
                not self.summary.is_package and not self.summary.is_pure_python_package

        self.summary.summary_save_path = self.save_path

        self.summary.file_update_times = self.get_file_update_times()
        self.resolve_package_class_dependencies()

        return

    @staticmethod
    def load_package_summary(package_in: str, save_path: str, pkg_logger: 'loguru.Logger') -> typing.Union['PackageSummary', None]:

        pkg_logger.bind(stage_log=True).info('Attempting to load {} package summary'.format(package_in))
        file_name = os.path.join(save_path, package_in.split('.')[-1] + str('.ips'))
        try:
            with open(file_name, 'rb') as summary_file:
                package_summary = pickle.load(summary_file)
        except:
            pkg_logger.bind(stage_log=True).info('{} package summary load failed'.format(package_in))
            return None

        pkg_logger.bind(stage_log=True).info('{} package summary load succeeded'.format(package_in))
        return package_summary

    @staticmethod
    def save_package_summary(package_summary: 'PackageSummary') -> None:

        pdb.set_trace()
        file_name = os.path.join(package_summary.summary_save_path, package_summary.ref.split('.')[-1] + '.ips')
        with open(file_name, 'wb') as summary_file:
            package_summary.merged_summary = None
            pickle.dump(package_summary, summary_file)

        return

    @fs.in_pkg_dir
    def collect_source(self) -> typing.List[typing.Tuple[str, int]]:

        self.pkg_logger.bind(stage_log=True).info('Collecting {} package source files'.format(self.illuminate_pkg_name))
        files_out = []
        for ext in self.source_ext:
            for file_with in fs.get_files_by_ext(ext, os.getcwd()):
                self.pkg_logger.bind(stage_log=True).info('Found source file {}'.format(file_with))
                files_out.append((file_with, BuildProtocol.COMPILE))
        return files_out

    @fs.in_pkg_dir
    def collect_py_source(self) -> typing.List[typing.Tuple[str, int]]:

        self.pkg_logger.bind(stage_log=True).info('Collecting {} package python source files'.format(self.illuminate_pkg_name))
        files_out = []
        for ext in self.py_source_ext:
            for file_with in fs.get_files_by_ext(ext, os.getcwd()):
                self.pkg_logger.bin(stage_log=True).info('Found python source file {}'.format(file_with))
                files_out.append((file_with, BuildProtocol.COPY))
        return files_out

    @fs.in_pkg_dir
    def collect_headers(self) -> typing.List[typing.Tuple[str, int]]:

        self.pkg_logger.bind(stage_log=True).info('Collecting {} package header files'.format(self.illuminate_pkg_name))
        files_out = []
        for ext in self.header_ext:
            for file_with in fs.get_files_by_ext(ext, os.getcwd()):
                self.pkg_logger.bind(stage_log=True).info('Found header file {}'.format(file_with))
                files_out.append((file_with, BuildProtocol.COMPILE))
        return files_out

    @fs.in_pkg_dir
    def collect_collection_files(self) -> typing.List[typing.Tuple[str, int]]:

        self.pkg_logger.bind(stage_log=True).info('Collecting {} package user-specified collection files'.format(self.illuminate_pkg_name))
        files_out = []
        for ext in self.collection_ext:
            for file_with in fs.get_files_by_ext(ext, os.getcwd()):
                self.pkg_logger.bind(stage_log=True).info('Found collection file {}'.format(file_with))
                files_out.append((file_with, BuildProtocol.PARSE))
        return files_out

    def __extend_files_to_check(self) -> typing.List[typing.Tuple[str, int]]:
        check_files = []
        check_files.extend(self.source)
        check_files.extend(self.headers)
        check_files.extend(self.py_source)
        check_files.extend(self.collection_files)
        return check_files

    @fs.in_pkg_dir
    def get_file_update_times(self) -> typing.Dict[str, int]:
        check_files = self.__extend_files_to_check()
        updates = {}
        for file_name, protocol in check_files:
            updates[file_name] = os.path.getmtime(file_name)
        return updates

    @fs.in_pkg_dir
    def get_files_to_update(self) -> typing.List[typing.Tuple[str, int]]:
       
        self.pkg_logger.bind(stage_log=True).info('Checking for files to update in {} package'.format(self.illuminate_pkg_name))
        check_files = self.__extend_files_to_check()
        updates = []
        
        update_times = self.get_file_update_times()

        if self.summary is None:
            for file_to_check in check_files:
                updates.append(file_to_check)
            return updates

        for file_name, protocol in check_files:
            try:
                if not self.summary.file_update_times[file_name] == update_times[file_name]:
                    self.pkg_logger.bind(stage_log=True).info('File {} requires updating'.format(file_name))
                    updates.append((file_name, protocol))
                    if protocol is BuildProtocol.COMPILE:
                        self.needs_recompile = True
            except KeyError:
                updates.append((file_name, protocol))
                self.needs_recompile = True

        return updates

    def collect_all_files(self, py_source_ext=[], source_ext=[], header_ext=[], collection_ext=[]) -> None:
        
        self.py_source_ext = ['.py']
        self.source_ext = ['.cpp', '.cc', '.c']
        self.header_ext = ['.hh', '.hpp', '.h']
        self.collection_ext = ['.ipc']

        self.py_source_ext.extend(py_source_ext)
        self.source_ext.extend(source_ext)
        self.header_ext.extend(header_ext)
        self.collection_ext.extend(collection_ext)

        self.py_source = self.collect_py_source()
        self.source = self.collect_source()
        self.headers = self.collect_headers()
        self.collection_files = self.collect_collection_files()

        return

    def resolve_package_class_dependencies(self) -> None:
      
        self.pkg_logger.bind(stage_log=True).info('Resolving {} package class dependencies'.format(self.illuminate_pkg_name))
        topo_sort = graphlib.TopologicalSorter()

        summary_classes = []
        for h_sum in self.summary.header_summaries:
            summary_classes.extend(h_sum.classes)
            summary_classes.extend(h_sum.template_classes)
            summary_classes.extend([pt.obj for pt in h_sum.partial_specializations if isinstance(pt.obj, ClassObject)])

        for class_obj in summary_classes:
            topo_sort.add(class_obj)
            for dep_class in class_obj.object_dependencies:
                if dep_class.dependency_resolved:
                    topo_sort.add(class_obj, dep_class.parse_object)
                    continue
                else:
                    self.pkg_logger.bind(logs_module_deps=True, header=class_obj.header.header_file) \
                        .info("Class {} has unresolved inheritance dependencies after processing. As a result, full \
                            account of inherited members and methods cannot be made.")
                    self.pkg_logger.bind(logs_module_deps=True, header=class_obj.header.header_file) \
                        .info("Inherited dependency {} of class {} cannot be found", dep_class.dep_name, 
                        class_obj.qualified_id)

        out = tuple(topo_sort.static_order())
        for class_idx, class_obj in enumerate(out):
            self.pkg_logger.bind(logs_module_deps=True, header=class_obj.header.header_file)\
                    .info("{}. {}".format(class_idx, class_obj.qualified_id))

        return out

    def search_for_original_py_class(self, name_str: str) -> typing.Tuple['ClassObject', str]:
        
        self.pkg_logger.bind(stage_log=True).info("Linking extension language class names with python class names")
        class_equivalents = self.summary.type_equivalents[name_str]

        original_class = None
        original_py_class = None
        for equiv in class_equivalents:
            if equiv.first_def:
                original_class = equiv.object
            if equiv.first_py_name:
                original_py_class = equiv.py_name

        return original_class, original_py_class

    def add_extern_pkg_dependency(self, pgk_name: str) -> None:
        self.pkg_logger.bind(stage_log=True).info('Adding extern package dependency {} to package {}'.format(
            pkg_name, self.illuminate_pkg_name))
        self.summary.add_inter_pkg_dependency(pkg_name)
        return

    def set_package_license_file(self, license_file: str) -> None:
        il_cfg.license_file = license_file
        return

    def _run_factories(self) -> None:
        for meta_factory in self.meta_factories:
            meta_factory(self, self.meta_dir)
        for ext_factory in self.extension_factories:
            ext_factory(self, self.extension_dir)
        if self.binding_factory is not None:
            self.binding_factory(self, self.binding_dir)
        return

