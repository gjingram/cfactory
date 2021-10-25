<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import os
    import graphlib
%>

<%page args="fmt, summary" expression_filter="trim"/>
<%inherit file="cpp_file.mako"/>
<%namespace name="includes" file="pybind11_includes.mako"/>

<%block name="includes">
// Pybind 11 includes
${includes.pybind11_module_includes()}

// Module include
<%
    module_include = summary.ref
    include_use = module_include
    for include_dir in mg.dash_eye:
        test_include = os.path.relpath(module_include,
            include_dir)
        if test_include.count(os.sep) < module_include.count(os.sep):
            include_use = test_include

    class ModuleData(object):
        def __init__(self):
            self.the_module = None
            self.the_parent = None
            self.desc = None
            return

    top_module = ModuleData()
    top_module.the_module = "m"
    top_module.the_parent = None

    namespace_to_module = {}
    namespace_to_module["top_ns"] = top_module
	
    namespace_to_module = {}
    for n_ns, ns in enumerate([nsl for nsl in summary.namespaces if nsl.id != "GlobalNamespace"]):
        new_sub = ModuleData()
        new_sub.the_module = f"m{n_ns}"
        new_sub.the_parent = ns.scope.qualified_id if ns.scope.qualified_id != "GlobalNamespace" \
            else "m"
        new_sub.desc = ns.brief if ns.brief is not None else None
        namespace_to_module[ns.qualified_id] = new_sub

    ns_sort = graphlib.TopologicalSorter()
    for scope_id, sub in namespace_to_module.items():
        if sub.the_parent == "m":
            ns_sort.add(sub, namespace_to_module["top_ns"]
        elif sub.the_parent is not None:
            ns_sort.add(sub, namespace_to_module[sub.the_parent])
        else:
            ns_sort.add(sub)
    ns_ordered = tuple(ns_sort.static_order())

%> 
#include "${include_use}"
</%block>

<%block name="code_gen">
namespace py = pybind11;

void init_${summary.ref| cf.fne}(py::module_ &m) {

    // Create modules for nested namespaces
    %for ns in ns_ordered if not ns.the_parent is None:
    %if ns.desc is not None:
    py::module_ ${ns.the_module} = ${ns.the_parent}.def_submodule(\
    "${ns.id}", "${ns.desc}");\
    %else:
    py::module_ ${ns.the_module} = ${ns.the_parent}.def_submodules(\
    "${ns.id}");\
    %endif
    %endfor

}
</%block>



