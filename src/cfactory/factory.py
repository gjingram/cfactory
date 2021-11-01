import os
import sys
import shutil
import time
from pathlib import Path
from warnings import warn
from typing import (
        Tuple,
        List,
        Optional
        )
import graphlib

import cfactory.__config__.cfactory_config as cfg
import cfactory.assemblers.assembler as assemblers
import cfactory.utils.file_sys as fs
import ccmodel.ccm as ccm_
import ccmodel.reader as ccm_reader
import pdb

# CFactory config
root = os.getcwd()
project_root = ""
cache_dir = os.path.join(
        os.getcwd(),
        "cfactory"
        )
cfactory_verbosity = 0
cfactory_clear_cache = False
cfactory_force = False
cfactory_mode = "cfactory"

# CCM config
ccm_state_dir = os.path.join(
        cache_dir,
        "ccm"
        )
clear_ccm = False
force_ccm = False
pretty_ccm = False
ccm_clang_opts = []
cfscripts = []

project_name = ""
project_license = ""

# File Options
max_cols = 80

# C File Options
c_max_cols = max_cols
c_header_ext = ".h"
c_source_ext = ".c"

# C++ File Options
cpp_max_cols = max_cols
cpp_header_ext = ".hh"
cpp_source_ext = ".cc"

meta_assemblers = []
meta_sorter = graphlib.TopologicalSorter()
meta_order = None

extension_assemblers = []
extension_sorter = graphlib.TopologicalSorter()
extension_order = None

finish_assemblers = []
finish_sorter = graphlib.TopologicalSorter()
finish_order = None

def ensure_abspaths() -> None:
    global root, project_root, cache_dir, ccm_state_dir
    root = fs.path_from_fs_root(root)
    if project_root == "":
        project_root = root
    else:
        project_root = fs.path_from_fs_root(project_root)
    cache_dir = fs.path_from_fs_root(cache_dir)
    ccm_state_dir = fs.path_from_fs_root(ccm_state_dir)
    return


class CCMAssembler(assemblers.Assembler, ccm_.CcmOpt):

    def __init__(self):
        assemblers.Assembler.__init__(self, "ccm", singleton=True)
        ccm_.CcmOpt.__init__(self)
        self.source_dependencies = set(all_source_dependencies())
        self.n_source_files = -1
        self.source_ccs = None
        self.ccs_catalogue = None
        self.headers = {}
        return

    def pre_assemble(self) -> None:
        self.get_ccm_recursion_level()
        self.default_ccm_configure()
        self.ccm_files = list(self.source_dependencies)
        self.n_source_files = len(self.ccm_files)

        if self.n_source_files < 1:
            cfg.cfactory_logger.info(
                    "CCM no source files specified.\n"
                    )
            return
        ccm_.ccm_opt = self
        ccm_.main()
        return

    def assemble(self) -> None:
        self.source_ccs = {}
        self.ccs_catalogue = {}
        reader = ccm_reader.CcsReader(self.out_dir)
        for src_dep in self.source_dependencies:
            ccs_file_dir = os.path.join(
                    self.out_dir,
                    os.path.dirname(src_dep.lstrip(os.sep))
                    )
            ccs_file_base = os.path.basename(src_dep)
            ccs_file_name = os.path.join(
                    ccs_file_dir,
                    ccs_file_base + ".ccs"
                    )
            self.headers[src_dep] = reader.read(ccs_file_name)
        self.source_ccs.update(reader._headers_loaded)
        self.ccs_catalogue.update(reader._ccs_catalogue)
        return

    def default_ccm_configure(self) -> None:
        self.verbosity = cfactory_verbosity
        self.out_dir = ccm_state_dir
        self.delete_out = clear_ccm
        self.force = force_ccm
        self.pretty = pretty_ccm
        return

    def get_ccm_recursion_level(self) -> None:
        for assembler in assemblers.registry.values():
            if assembler._ccm_rlevel > self.recursion_level:
                self.recursion_level = assembler._ccm_rlevel
            if self.recursion_level == assemblers.CCMRecursionLevel.FULL:
                break
        self.process_main_includes = self.recursion_level < 1
        return

    def __getitem__(
            self,
            header: str) -> Optional["ccmodel.code_models.header.Header"]:
        if header in self.headers:
            return self.headers[header]
        cfg.cfactory_logger.bind(color="orange").opt(colors=True).warn(
                "No CCModel state file found for header: " + "\n" +
                f"{header} in {self.out_dir}" + "\n"
                )
        return None

def ccm_out_exists() -> bool:
    return os.path.exists(ccm_state_dir)

def cfactory_cache_exists() -> bool:
    return os.path.exists(cache_dir)

def ensure_cfactory_cache() -> None:
    if not cfactory_cache_exists():
        Path(cache_dir).mkdir(parents=True)
    elif cfactory_clear_cache:
        shutil.rmtree(cache_dir)
        Path(cache_dir).mkdir(parents=True)
    return

def all_source_dependencies() -> List[str]:
    out = []
    for assembler in assemblers.registry.values():
        out.extend(assembler.source_dependencies)
    return list(set(out))

def all_source_emitted() -> List[str]:
    out = []
    for assembler in assemblers.registry.values():
        out.extend(assembler.source_emitted)
    return list(set(out))

def cfscript_in_root() -> bool:
    return "cfscript.py" in os.listdir(root)

def categorize_assemblers() -> None:
    for assembler in assemblers.registry.values():
        if isinstance(assembler, assemblers.MetaStage):
            meta_assemblers.append(assembler)
        elif isinstance(assembler, assemblers.ExtensionStage):
            extension_assemblers.append(assembler)
        elif isinstance(assembler, assemblers.FinishStage):
            finish_assemblers.append(assembler)
        else:
            cfg.cfactory_logger.bind(color="orange").opt(colors=True).warn(
                    "Unrecognized assembler base type for assembler: " +
                    f"{assembler.assembler_name}" + "\n" +
                    f"Assembler type: {type(assembler).__name__}" + "\n" +
                    "Skipping"
                    )
    return

def resolve_assembler_deps() -> None:
    for ma in meta_assemblers:
        meta_sorter.add(ma, ma.assembler_dependencies)
    if len(meta_assemblers):
        meta_order = tuple(meta_sorter.static_order())
    for ea in extension_assemblers:
        extension_sorter.add(ea, ea.assembler_dependencies)
    if len(extension_assemblers):
        extension_order = tuple(extension_sorter.static_order())
    for fa in finish_assemblers:
        finish_sorter.add(fa, fa.assembler_dependencies)
    if len(finish_assemblers):
        finish_order = tuple(finish_sorter.static_order())
    return


ccm = CCMAssembler()
def ccmodel_assemble() -> None:
    tic = time.perf_counter()
    categorize_assemblers()
    resolve_assembler_deps()
    ccm.pre_assemble()
    ccm.assemble()
    toc = time.perf_counter()
    cfg.cfactory_logger.bind(color="green").opt(colors=True).info(
            f"CCM assembly complete in {toc - tic} [s]\n"
            )
    print()
    return

def factory_assemble() -> None:

    if cfactory_clear_cache:
        shutil.rmtree(cache_dir)

    ccmodel_assemble()

    factory_tic = time.perf_counter()
    for assembler in assemblers.registry.values():
        assembler.pre_assemble()

    if meta_order is not None:
        for ma in meta_order:
            tic = time.perf_counter()
            ma.assemble()
            ma.post_assemble()
            toc = time.perf_counter()
            cfg.cfactory_logger.info(
                    f"{ma.assembler_name} assembly complete in {toc - tic} [s]\n"
                    )
    else:
        cfg.cfactory_logger.info(
                "No meta assemblers specified\n"
                )
    print()

    if extension_order is not None:
        for ea in extension_order:
            tic = time.perf_counter()
            ea.assemble()
            toc = time.perf_counter()
            cfg.cfactory_logger.info(
                    f"{ea.assembler_name} assembly complete in {toc - tic} [s]\n"
                    )
    else:
        cfg.cfactory_logger.info(
                "No extension assemblers specified\n"
                )
    print()

    if finish_order is not None:
        for fa in finish_order:
            tic = time.perf_counter()
            fa.assemble()
            toc = time.perf_counter()
            cfg.cfactory_logger.info(
                    f"{fa.assembler_name} assembly complete in {toc - tic} [s]\n"
                    )
    else:
        cfg.cfactory_logger.info(
                "No finish assemblers specified\n"
                )
    print()
    factory_toc = time.perf_counter()
    cfg.cfactory_logger.bind(color="green").opt(colors=True).info(
            f"Factory assemble complete in {factory_toc - factory_tic} [s]\n"
            )
    return
