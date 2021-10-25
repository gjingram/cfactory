<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.code_models.class_object as co
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
%>

<%page args="enum, cls_instance_in" expression_filter="trim"/>

<%def name="write_enum(enum_in, cls_instance=None)" decorator="cp.check_opt" filter="trim">
<%
    enum_name = enum_in.pyname
%>
py::enum_<${enum_in.qualified_id}>\
%if cls_instance is not None:
(${cls_instance}, "${enum_name}")\
%else:
("${enum_name}")\
%endif
%for field in enum.enum_fields:
.value("${field.pyname}", ${field.qualified_id})\
%endfor
%if not enum.get_enum_scoped():
.export_values()\
%endif
</%def>

${write_enum(enum, cls_instance_in)}
