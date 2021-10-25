<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
%>

<%page expression_filter="trim"/>

<%def name="pybind11_top_includes()" filter="trim">
#include <pybind11/pybind.h>
</%def>

<%def name="pybind11_module_includes()" filter="trim>
#include <pybind11/pybind.h>
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/eigen.h>
#include <pybind11/embed.h>
#include <pybind11/eval.h>
#include <pybind11/functional.h>
#include <pybind11/iostream.h>
#include <pybind11/options.h>
#include <pybind11/stl.h>
</%def>
