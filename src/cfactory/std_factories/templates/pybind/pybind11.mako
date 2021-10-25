<%!
    import illuminate.machines.file_formatter as ff
    import illuminate.machines.common_filters as cf
    import illuminate.code_models.class_object as co
%>

<%page args="file_data, format"/>

<%
    fmat = ff.FileFormatter(file_data, fmt)
    class_ids = {}
    class_conversions = {}
%>

<%def name="str_list(strings)">
%for string in strings:
%{string} \
%endfor
</%def>

<%def name="write_fparam(param)">
py::arg("${param.get_name()}") \
%if param.noconvert:
.noconvert() \
%endif
%if param.disallow_none:
.none(false) \
%endif
%if param.default is not None:
= ${param.default} \
%endif
</%def>

<%def name="extract_fparams(func)">
%for param in func.parameter_list:
${write_fparam(param)} \
%endfor
%if func.rvp:
${func.rvp} \
%endif
%if func.brief:
${func.brief} \
%endif
%for keep_alive in func.keep_alive:
py::keep_alive<${keep_alive[0]}, ${keep_alive[1]}>() \
%endfor
%if len(func.scope_guards):
py::call_guard<${str_list(func.scope_guard) | trim,cf.plfsl,cf.stc}>() \
%endif
%if func.priority_overload:
py::prepend()
%endif
</%def>

<%def name="write_function_ptr(func, is_method=False)">
%if is_method:
static_cast<${func.return_type} (${func.scope.qualified_id}::*) \
%else:
static_cast<${func.return_type} (*) \
%endif
( \
${str_list([x.type for x in func.parameter_list]) | trim,cf.plfsl,cf.stc} \
)>(&${func.qualified_id})
</%def>

<%def name="write_function(name, func, is_method=False)">
%if not is_method:
m \
%endif
.def(${str_list(["name", write_function_ptr(func, is_method), extract_fparams(func)]) | trim,cf.plfsl,cf.stc,fmat.fl});
</%def>

<%def name="write_var(var)">
m.attr(${var.qualified_id} = ${var.qualified_id};
</%def>

<%def name="write_enum(enum)">
py::enum_<${enum.qualified_id}> \
%if isinstance(enum.scope, co.ClassObject):
(${class_ids[enum.scope.qualified_id]}, "${enum.pyname}") \
%else
(${enum.pyname}) \
%endif
%for field in enum.enum_fields:
.value("${field.get_name()}", ${field.qualified_id}) \
%endfor
%if enum.get_enum_scoped():
.export_values();
%endif

<%def name="write_member_function(func)">
%if func.is_ctor:
.def(${str_list([py::init<${str_list([param.type for param in func.parameter_list]) | trim,cf.plfsl,cf.stc}>(), extract_fparams(func)]) | trim,cf.plfsl,cf.stc,fmat.fl})
%elif func.magic:
.def("${func.magic_name}", &${func.qualified_id}, py::operator())
%elif func.is_conversion:
<%
if func.scope.qualified_id not in class_conversions:
    class_conversions[func.scope.qualified_id] = []
class_conversions[func.scope.qualified_id].append(func.return_type)
%>








