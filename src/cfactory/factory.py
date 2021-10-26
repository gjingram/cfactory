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
import cfactory.assembler as assemblers
import cfactory.utils.file_sys as fs
import ccmodel.ccm as ccm_
import ccmodel.reader as ccm_reader

# CFactory config
root = os.getcwd()
cache_dir = os.path.join(
        os.getcwd(),
        "cfactory"
        )
cfactory_verbosity = 0
cfactory_clear_cache = False
cfactory_force = False

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

meta_assemblers = []
meta_sorter = graphlib.TopologicalSorter()
meta_order = None

extension_assemblers = []
extension_sorter = graphlib.TopologicalSorter()
extension_order = None

finish_assemblers = []
finish_sorter = graphlib.TopologicalSorter()
finish_order = None


class CCMAssembler(assemblers.Assembler, ccm_.CcmOpt):

    def __init__(self):
        assemblers.Assembler.__init__(self, "ccm", singleton=True)
        ccm_.CcmOpt.__init__(self)
        self.source_dependencies = set(all_source_dependencies())
        self.source_ccs = None
        self.ccs_catalogue = None
        self.headers = {}
        return

    def pre_assemble(self) -> None:
        self.get_ccm_recursion_level()
        self.default_ccm_configure()

        self.ccm_files = list(self.source_dependencies)
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
        self.source_ccs.update(reader.headers_loaded)
        self.ccs_catalogue.update(reader._ccs_catalogue)
        return

    def default_ccm_configure() -> None:
        self.verbosity = cfactory_verbosity
        self.out_dir = ccm_state_dir
        self.delete_out = clear_ccm
        self.force = force_ccm
        self.pretty = pretty_ccm
        return

    def get_ccm_recursion_level() -> None:
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
        # Logger warn
        return None

ccm = CCMAssembler()

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
            # Logger warn
    return

def resolve_assembler_deps() -> None:
    for ma in meta_assemblers:
        meta_sorter.add(ma, ma.assembler_dependencies)
    if len(ma):
        meta_order = tuple(meta_sorter.static_order())
    for ea in extension_assemblers:
        extension_sorter.add(ea, ea.assembler_dependencies)
    if len(ea):
        extension_order = tuple(extension_sorter.static_order())
    for fa in finish_assemblers:
        finish_sorter.add(fa, fa.assembler_dependencies)
    if len(fa):
        finish_order = tuple(finish_sorter.static_order())
    return

def ccmodel_assemble() -> None:
    categorize_assemblers()
    resolve_assembler_deps()
    ccm.pre_assemble()
    ccm.assemble()
    return

def factory_assemble() -> None:

    if cfactory_clear_cache:
        shutil.rmtree(cache_dir)

    ccmodel_assemble()

    for assembler in assemblers.registry.values():
        assembler.pre_assemble()

    for ma in meta_order:
        ma.assemble()
        ma.post_assemble()
    for ea in extension_order:
        ea.assemble()
    for fa in finish_order:
        fa.assemble()

    return
