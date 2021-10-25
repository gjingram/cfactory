<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
%>

<%page args="mfunc" expression_filter="trim"/>
<%namespace name="func" file="function.mako"/>
<%namespace name="fparam" file="fparam.mako"/>
<%namespace name="utils" file="util_defs.mako"/>


<%def name="extract_ctor_params(ctor)" decorator="cp.check_opt" filter="trim">
%for param in ctor.info['args']:
${fparam.write_fparam(ctor.info['args'][param])} \
%endfor
%if ctor.brief:
"${ctor.brief}" \
%endif
%for keep_alive in ctor.pybind.keep_alive:
py::keep_alive<${keep_alive[0]}, ${keep_alive[1]}>() \
%endfor
%if len(ctor.pybind.scope_guards):
py::call_guard<\
${capture(utils.str_list, ctor.pybind.scope_guards)| trim, cf.plfsl, cf.stc}>()
%endif
</%def>\

<%def name="write_ctor_args(ctor)" decorator="cp.check_opt" filter="trim">
py::init<${capture(utils.str_list, [x.type for x in ctor.info['args'].values()])}>() \
${capture(extract_ctor_params, ctor)}\
</%def>

<%def name="write_ctor(ctor)" decorator="cp.check_opt" filter="trim">
def(${capture(write_ctor_args, ctor)| cf.plfsl, cf.stc})
</%def>

<%def name="write_magic_method(method)" decorator="cp.check_opt" filter="trim">
${capture(func.write_function, method, fn_name=method.magic_name)| trim}\
</%def>\

<%def name="write_factory_method(method)" decorator="cp.check_opt" filter="trim>
def(py::init(&${method.qualified_id})\
</%def>\

<%def name="write_conversion(method)" decorator="cp.check_opt" filter="trim">
<%
    ret_unqualified = method.return_type.replace('&', '').replace('*', '')
    ret_unqualified.strip()
    ret_type = ""
    for token in ret_unqualified:
        if token != "const":
            ret_type += token
    ret_type.strip()

    convertible = ret_type in mg.class_ids.values()
    if not convertible:
        try:
            ret_type = mg.class_ids[ret_type]
            convertible = True
        except:
            pass
%>
%if convertible:
py::implicitly_convertible<${method.scope.pyname}, ${method.return_type}>()\
%endif
</%def>\

<%def name="write_method(method)" decorator="cp.check_opt" filter="trim">
${func.write_function(method)}\
</%def>

%if not method.is_pure_virtual:
%if method.is_ctor:
${write_ctor(method)}\
%elif method.pybind.factory_method:
${write_factory_method(method)}\
%elif method.is_conversion:
${write_conversion(method)}\
%elif method.magic:
${write_magic_method(method)}\
%elif not method.is_dtor:
${write_method(method)} \
%endif
%endif
