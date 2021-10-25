<%!
    import illuminate.std_factories.file_formatter as ff
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.check_pybind as cp
%>
<%page args="var"/>

<%def name="write_var(var_in)" decorator="cp.check_opt" filter="trim">
m.attr("${var_in.pyname}") = ${var_in.qualified_id};\
</%def>

${write_var(var)}
