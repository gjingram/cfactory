import sys
import os
import pathlib
import typing
import functools
import pdb

import illuminate.__config__.illuminate_config as ilc

def check_subproject_exists(method):

    @functools.wraps(method)
    def _check_subproject_exists(self, sub_project_name: str, *args) -> None:
        if not sub_project_name in self.registered_sub_projects.keys():
            raise RuntimeError('No sub project named {} registered with project config!' \
                    .format(sub_project_name))
        method(self, sub_project_name, *args)
        return
    return _check_subproject_exists

class ProjectConfig(object):

    def __init__(self, project_name: str, project_path: str=None):

        self.project_name = project_name
        self.project_path = os.getcwd() if project_path is None else project_path

        self.registered_sub_projects = {}
        self.python_paths = {}
        self.include_directories = {}
        self.lib_directories = {}
        self.ld_lib_directories = {}
        self.rpath_directories = {}

        project_config = self

        return

    def register_sub_project(self, sub_project_name: str, root_dir: str) -> None:
        if not sub_project_name in self.registered_sub_projects.keys():
            self.registered_sub_projects[sub_project_name] = root_dir
        return

    @check_subproject_exists
    def add_include_directory(self, spn: str, include_dir: str) -> None:
        if not spn in self.include_directories.keys():
            self.include_directories[spn] = []
        self.include_directories[spn].append(include_dir)
        return

    def get_include_directories(self) -> typing.List[str]:
        return [idir for idir in self.include_directories.values()]

    @check_subproject_exists
    def add_lib_directory(self, spn: str, lib_dir: str) -> None:
        if not spn in self.lib_directories.keys():
            self.lib_directories[spn] = []
        self.lib_directories[spn].append(lib_dir)
        return

    def get_lib_directories(self) -> typing.List[str]:
        return [ldir for ldir in self.lib_directories.values()]

    @check_subproject_exists
    def add_ld_lib_directory(self, spn: str, ld_lib_dir: str) -> None:
        if not spn in self.lib_directories.keys():
            self.ld_lib_directories[spn] = []
        self.ld_lib_directories[spn].append(ld_lib_dir)
        return

    def get_ld_lib_directories(self) -> typing.List[str]:
        return [ldlib for ldlib in self.ld_lib_directories.values()]

    @check_subproject_exists
    def add_rpath_directory(self, spn: str, rpath_dir: str) -> None:
        if not spn in self.rpath_directories.keys():
            self.rpath_directories[spn] = []
        self.rpath_directories[spn].append(rpath_dir)
        return

    def get_rpath_directories(self) -> typing.List[str]:
        return [rpath for rpath in self.rpath_directories.values()]

project_config = None
