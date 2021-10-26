import sys
import glob

registry = {}

def manager_add_assembler(assembler: "Assembler") -> None:
    if assembler.is_singleton:
        assembler_key = type(assembler).__name__
        if assembler_key in registry:
            if not register[assembler_key].merge_assembler(assembler):
                # Logger error
                sys.exit(-1)
    else:
        if assembler.assembler_name in registry:
            # Logger error
            sys.exit(-1)
        else:
            registry[assembler.assembler_name] = assembler
    return


class CCMRecursionLevel(object):

    def __init__(self):
        INVALID = -1
        NONE = 0
        INHERITED = 1
        FULL = 2
        return


class Assembler(object):

    def __init__(self, name: str, singleton: bool = False):
        self.is_singleton = singleton
        self.assembler_name = name
        self.assembler_dependencies = set()
        self.source_dependencies = set()
        self.source_emitted = set()
        self._ccm_rlevel = CCMRecursionLevel.INVALID
        manager_add_assembler(self)
        return

    def dependency_recurse(self, dep_in: "Assembler") -> bool:
        for dep in self.assembler_dependencies:
            if (
                    dep is dep_in or
                    dep.dependency_recurse(dep_in)
                    ):
                return True
        return False

    def _check_dependency_valid(self, dep: "Assembler", fatal: bool = True) -> bool:
        if self in dep.assembler_dependencies:
            if fatal:
                # Logger error
                sys.exit(-1)
            else:
                return False
        return True

    def _emit_source(self, src: str) -> None:
        self.source_emitted.add(src)
        return

    def add_dependency(self, dep: "Assembler") -> None:
        if self._check_dependency_valid(dep):
            self.assembler_dependencies.add(dep)
        return

    def add_source_dependency(self, dep: str) -> None:
        deps = glob.glob(dep)
        for dep in deps:
            self.source_dependencies.add(dep)
        return

    def pre_assemble(self) -> None:
        pass

    def assemble(self) -> None:
        pass

    def merge_assembler(self, other: "Assembler") -> bool:
        if (
                self.dependency_recurse(other) or
                any(
                    [
                        self.dependency_recurse(x) for x in
                        other.assembler_dependencies
                        ]
                    )
                ):
            return False
        self.assembler_dependencies.union(other.assembler_dependencies)
        self.source_dependencies.union(other.source_dependencies)
        return True


class MetaStage(Assembler):

    def __init__(self, name: str):
        super().__init__(name)
        return

    def _check_dependency_valid(self, dep: Assembler) -> bool:
        Assembler._check_dependency_valid(self)
        if (
                isinstance(dep, ExtensionStage) or
                isinstance(dep, FinishStage)
                ):
            # Logger error
            sys.exit(-1)
        return True

    def post_assemble(self) -> None:
        pass


class ExtensionStage(Assembler):

    def __init__(self, name: str):
        super().__init__(name)
        return

    def _check_dependency_valid(self, dep: Assembler) -> bool:
        Assembler._check_dependency_valid(self)
        if isinstance(dep, FinishStage):
            # Logger error
            sys.exit(-1)
        elif isinstance(dep, MetaStage):
            return False
        return True


class FinishStage(Assembler):

    def __init__(self, name: str):
        super().__init__(name)
        return

    def _check_dependency_valid(self, dep: Assembler) -> bool:
        Assembler._check_dependency_valid(self)
        if not isinstance(dep, FinishStage):
            return False
        return True
