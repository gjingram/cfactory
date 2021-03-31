import os
import sys
import typing
import importlib.util as ilu
import importlib.machinery as ilm
import graphlib
import types
import copy
import pdb

import illuminate.__config__.illuminate_config as ilc
import illuminate.utils.file_sys as fs
import illuminate.collections.illuminate_package as ip
import illuminate.collections.project_config as pc
import illuminate.std_factories.factory as factory

def get_pkg_parts(dir_path, root) -> typing.Tuple[str, str]:
    rel_path = os.path.relpath(dir_path, start=root)
    return (rel_path.replace(os.path.sep, '.'), dir_path)

def get_rel_path(dir_path, root) -> typing.Union[str, None]:
    rel_path = os.path.replath(dir_path, start=root)
    return rel_path


class IlluminateProject(object):

    sys.path.append(os.getcwd())

    typedefs = {}

    def __init__(self, config: pc.ProjectConfig):

        self.project_config = config
        self.project_name = config.project_name

        self.proj_logger = ilc.logger.bind(project=self.project_name, stage_log=True)

        self.packages_discovered = {}
        self.namespace_level_packages = {}

        self.c_cpp_compiler_args = {}

        for sub_proj in self.project_config.registered_sub_projects.keys():
            self.c_cpp_compiler_args[sub_proj] = []
            self.packages_discovered[sub_proj] = []

        self.extract_compiler_args()
        self.packages = []

        self.binding_factory = None
        self.extension_factories = []
        self.meta_factories = []

        self.binding_dir = ""
        self.extension_dir = ""
        self.meta_dir = ""
        self.factory_out_dir = ""

        self._active_namespace = ""

        self.__pkg_config_ext = ".ipc"

        return

    def set_active_namespace(self, ns: str) -> None:
        self.active_namespace = ns
        return

    def add_typedef(self, qid: str, name: str, exists: bool = False) -> None:
        parts = (self.active_namespace + "::" + qid).split("::")
        dict_use = IlluminateProject.typedefs
        key = ""
        for part in parts[1:]:
            if not part in dict_use:
                dict_use[part] = {
                        "typedefs": []
                        }
            if part == parts[-2]:
                dict_use[part]["typedefs"].append((parts[-1], name, exists))
                break
            else:
                dict_use = dict_use[part]
        return

    def add_factory(self, factory_cls) -> None:
        if factory_cls.factory_type == factory.FactoryType.BINDING:
            self.binding_factory = factory_cls
        elif factory_cls.factory_type == factory.FactoryType.EXTENSION:
            self.extension_factories.append(factory_cls)
        elif factory_cls.factory_type == factory.FactoryType.META:
            self.meta_factories.append(factory_cls)
        return

    def extract_compiler_args(self) -> None:

        for sub_proj, include_dirs in self.project_config.include_directories.items():
            for include_dir in include_dirs:
                self.c_cpp_compiler_args[sub_proj].extend(['-I', include_dir])

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

    def process_project(self) -> None:
        self.proj_logger.info("Creating project: {}".format(self.project_name))
        self.discover_all_packages()
        for pkg_list in self.packages_discovered.values():
            for pkg in pkg_list:
                pkg.process_package()
                self.resolve_project_package_dependencies()
                self.resolve_project_class_dependencies()
                ip.IlluminatePackage.save_package_summary(pkg.summary)
        return

    def discover_all_packages(self) -> None:

        self.proj_logger.info("Searching for packages")
        for sub_proj, directory in self.project_config.registered_sub_projects.items():
            for dir_path, dir_names, file_names in os.walk(directory):
                for file_name in file_names:
                    if file_name.endswith(self.__pkg_config_ext):
                        self.proj_logger.info("Found package at {}".format(dir_path))
                        self.import_pkg_config(sub_proj, dir_path, file_name, directory)
        return

    def import_pkg_config(self, sub_proj: str, dir_path: str, module_name: str, project_root: str) -> None:

        # load config module
        config_module_path = os.path.join(dir_path, module_name)
        config_module_name = sub_proj + '.' + os.path.relpath(dir_path, project_root).replace(os.sep, '.') + \
            '.' + module_name.split('.')[0]

        sys.dont_write_bytecode = True
        spec = ilu.spec_from_loader(config_module_name, ilm.SourceFileLoader(config_module_name, config_module_path))
        config_module_actual = ilu.module_from_spec(spec)
        spec.loader.exec_module(config_module_actual)
        sys.dont_write_bytecode = False

        
        # pass top-level compiler args, process & save package
        if config_module_actual.package.inherits_c_cpp_compiler_args:
            pkg_compiler_args = copy.copy(self.c_cpp_compiler_args[sub_proj])
            pkg_compiler_args.extend(config_module_actual.package.c_cpp_compiler_args)
            config_module_actual.package.c_cpp_compiler_args = pkg_compiler_args
        
        if config_module_actual.package.inherits_binding_factory:
            config_module_actual.package.add_factory(self.binding_factory)

        if config_module_actual.package.inherits_extension_factories:
            for f in self.extension_factories:
                config_module_actual.package.add_factory(f)

        if config_module_actual.package.inherits_meta_factories:
            for f in self.meta_factories:
                config_module_actual.package.add_factory(f)

        if config_module_actual.package.inherits_factory_dir:
            config_module_actual.package.set_factory_directory(self.factory_out_dir)
        if config_module_actual.package.inherits_binding_dir:
            config_module_actual.package.set_binding_directory(self.binding_dir)
        if config_module_actual.package.inherits_extension_dir:
            config_module_actual.package.set_extension_directory(self.extension_dir)
        if config_module_actual.package.inherits_meta_dir:
            config_module_actual.package.set_meta_directory(self.meta_dir)

        self.packages_discovered[sub_proj].append(config_module_actual.package)

        return

    def resolve_project_package_dependencies(self) -> None:
       
        self.proj_logger.info("Resolving project package dependencies for {}".format(self.project_name))
        topo_sort = graphlib.TopologicalSorter()
        
        for proj in self.project_config.registered_sub_projects.keys():
            for pkg_obj in self.packages_discovered[proj]:
                topo_sort.add(pkg_obj)
                for ext_header in pkg_obj.summary.external_headers:
                    pkg_dep = self.search_packages_for_header(ext_header)
                    pkg_obj.summary.add_inter_pkg_dependency(pkg_dep)
                    topo_sort.add(pkg_obj, pkg_dep)

        out = tuple(topo_sort.static_order())
        for pkg_idx, pkg in enumerate(out):
            self.proj_logger.info("{}. {}".format(pkg_idx, pkg.illuminate_pkg_name))

        return out

    def resolve_project_class_dependencies(self) -> None:

        self.proj_logger.info("Resolving project {} class dependencies".format(self.project_name))

        pkgs_resolved = []
        for proj in self.project_config.registered_sub_projects.keys():
            for pkg in self.packages_discovered[proj]:
                for extern_pkg in pkg.summary.inter_package_dependencies:
                    pkg.summary.header_summaries.extend(extern_pkg.header_summaries)
                if not pkg in pkgs_resolved:
                    pkg.resolve_package_class_dependencies()
        return
