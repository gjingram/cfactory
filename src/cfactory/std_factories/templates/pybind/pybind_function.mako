<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.check_pybind as cp
    from illuminate.pybind.enumerations import value_policy_map
%>

<%page args="function" expression_filter="trim"/>

<%namespace name="utils" file="util_defs.mako"/>
<%namespace name="fparam" file="fparam.mako"/>

<%def name="extract_fparams(func)" decorator="cp.check_opt" filter="trim">
%for param in func.info['args']:
${fparam.write_fparam(func.info['args'][param])} \
%endfor
%if func.pybind.rvp:
${value_policy_map[func.pybind.rvp]} \
%endif
%if func.brief:
"${func.brief}" \
%endif
%for keep_alive in func.pybind.keep_alive:
py::keep_alive<${keep_alive[0]}, ${keep_alive[1]}>() \
%endfor
%if len(func.pybind.scope_guards):
py::call_guard<\
${capture(utils.str_list, func.pybind.scope_guards)| trim,cf.plfsl,cf.stc}>() \
%endif
%if func.pybind.priority_overload:
py::prepend()
%endif
</%def>\

<%def name="write_function_ptr(func)" decorator="cp.check_opt" filter="trim">
%if func._is_member and func.scope.get_name() != "GlobalNamespace":
%if not func.is_ctor:
static_cast<${func.return_type} (${func.scope.qualified_id}::*)\
%endif
%else:
static_cast<${func.return_type} (*)\
%endif
(\
${capture(utils.str_list, [x.type for x in func.info['args'].values()])| trim,cf.plfsl, cf.stc}\
)\
%if func._is_member:
%if func.is_const:
 const\
%endif
%endif
>(&${func.qualified_id})\
</%def>

<%def name="write_function(func, fn_name=None)" decorator="cp.check_opt" filter="trim">
%if not func._is_member:
m.\
%endif
def(\
%if fn_name is None:
"${func.pyname| trim}", \
%else:
"${fn_name}", \
%endif
${write_function_ptr(func)| trim}, \
${capture(extract_fparams, func)| trim,cf.plfsl}\
)\
</%def>

${capture(write_function, function)}
