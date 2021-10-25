import typing
import copy
import pdb

import illuminate.rules.code_model_map as cmm

class UnitSummary(object):

    def __init__(self):

        self.ref = ""
        self.namespaces = []
        self.classes = []
        self.unions = []
        self.enumerations = []
        self.variables = []
        self.functions = {}
        self.template_classes = []
        self.partial_specializations = []
        self.template_functions = {}
        self.template_aliases = []
        self.typedefs = []
        self.namespace_aliases = []
        self.using = []
        self.extern_headers = []
        self.unit_headers = []
        self.comments = {}
        self.long_desc = ""
        self.brief = ""
        self.pyname_map = {}
        self.all_objects = []

        self.identifier_map = {}
        self.usr_map = {}

        return

    def __getitem__(self, item: str) -> 'ParseObject':
        return self.usr_map[self.identifier_map[usr]]

    def get_usr(self, usr: str) -> 'ParseObject':
        return self.usr_map[usr]

    def usr_in_summary(self, usr: str) -> bool:
        return usr in self.usr_map

    def get_original_cpp_object(self, name: str) -> 'ParseObject':
        pass 

    def get_extern_includes(self) -> typing.List[str]:
        return self.extern_headers

    def get_includes(self) -> typing.List[str]:
        return self.unit_headers

    def get_global_scope(self) -> 'NamespaceObject':
        for ns in self.namespaces:
            if ns.get_name() == "GlobalNamespace":
                return ns

FunctionHint = typing.Union[typing.Tuple[str, typing.List[str]], \
        typing.Tuple[str, typing.List[str], bool]]

class PackageSummary(object):

    def __init__(self, summaries_in: typing.List[UnitSummary]):

        self.py_source = []
        self.source = []
        self.internal_headers = []
        self.external_headers = []
        self.collection_files = []
        self.subdirectories = []
        self.is_extension = False
        self.is_package = False
        self.is_pure_python_package = False
        self.is_namespace = False
        self.intern_deps_resolved = False
        self.extern_deps_resolved = False
        self.summary_save_path = ""

        self.header_summaries = []

        self.file_update_times = {}
        self.intra_package_dependencies = None
        self.inter_package_dependencies = set([])

        self.using_code_models = cmm.default_code_models

        return

    def add_inter_pkg_dependency(self, ext_pkg: str) -> None:
        self.inter_package_dependencies.add(ext_pkg)
        return

    def __getitem__(self, search_item: typing.Union[str, FunctionHint]) -> 'ParseObject':

        if type(search_item) is str:
            out = None
            try:
                out = self.identifier_map[search_item]
            except KeyError:
                il_cfg.logger.error('PackageSummary.__getitem__ error, no such object \
                        {}'.format(search_item))
                raise RuntimeError
            return out
        
        search_name = search_item[0]
        is_const = False
        if len(search_item) >= 2:
            str_joined = ",".join(search_item[1])
            str_joined = "".join(str_joined.split())
            search_name = search_name + '(' + str_joined + ')'

        if len(search_item) == 3 and search_item[2]:
            search_name = search_name + 'const'
            is_const = True

        out = None
        for key, val in self.identifier_map.items():
            key_no_ws = "".join(key.split())
            if key_no_ws == search_name:
                return self.identifier_map[key]

        pretty_fn_name = search_item[0] + '(' + ", ".join(search_item[1]) + ')'
        pretty_fn_name = pretty_fn_name + ' const' if is_const else pretty_fn_name

        il_cfg.logger.error('PackageSummary.__getitem__ error, no such object \
                {}'.format(pretty_fn_name))
        raise RuntimeError

        return out
