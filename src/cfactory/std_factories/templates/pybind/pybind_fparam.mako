<%!
    import illuminate.std_factories.file_formatter as ff
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.check_pybind as cp
%>

<%page args="fparam" expression_filter="trim"/>

<%def name="write_fparam(param)" decorator="cp.check_opt" filter="trim">
%if not param.anonymous and not param.pybind.is_args and not param.pybind.is_kwargs and not param.pybind.no_kwarg:
py::arg("${param.get_name()}")\
%if param.pybind.no_convert:
.noconvert()\
%endif
%if param.pybind.disallow_none:
.none(false)\
%endif
%if param.default is not None and not param.pybind.ignore_default:
 = ${param.default}\
%endif
%endif
</%def>\

${write_fparam(fparam)}
