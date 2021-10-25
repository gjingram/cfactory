<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
    from illuminate.std_factories.lambda import 
    import pdb
%>

<%page args="expr" expression_filter="trim"/>
<%namespace name="utils" file="util_defs.mako"/>

<%def name="write_lambda_captures(caps)" filter="trim, cf.plfsl, cf.stc">
%for capture in caps:
${capture} \
%endfor
</%def>

<%def name="write_lambda_params(params)" filter="trim, cf.plfsl, cf.stc">
%for param in params:
${param} \
%endfor
</%def>

<%def name="default_lambda_getter(var)" filter="trim">
[]\
(${var.scope.qualified_id} const &cls) -> ${var.type} {
    return cls.${var.id};
}
</%def>

<%def name="default_lambda_setter(var)" filter="trim">
[]\
(${var.scope.qualified_id} &cls, ${var.type} set) -> void {
    cls.${var.id} = set;
    return;
}
</%def>

<%def name="union_casting_getter(union_name, data_name, field_type)" filter="trim">
[](${union_name} const &union) -> ${field_type} {
    return reinterpret_cast<${field_type}>(*(union.${data_name}));
}
</%def>

<%def name="union_casting_setter(union_name, data_name, field_type)" filter="trim">
[](${union_name} &union, ${field_type} set) -> void {
    *(reinterpret_cast<${field_type} *>(union.${data_name})) = set;
    return;
}
</%def>
