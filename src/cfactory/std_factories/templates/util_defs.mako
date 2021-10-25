<%!
    import illuminate.std_factories.file_formatter as ff
    import illuminate.std_factories.common_filters as cf
%>

<%def name="str_list(strings)" filter="trim">
%for string in strings:
${string|trim} \
%endfor
</%def>
