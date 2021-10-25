<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
%>

<%page args="fmt, summary"/>
<%inherit file="cpp_file.mako"/>
<%namespace name="includes" file="pybind11_includes.mako"/>

<%block name="includes">
// Pybind 11 Includes
${includes.pybind11_top_includes()}
</%block>

<%block name="code_gen">
namespace py = pybind11;

// Prototypes for individual header binding functions
%for header in summary.unit_headers:
void init_${header| cf.filename_no_ext}(py::module_ &); // See pybind/${header| cf.filename_no_ext}.${fmt.src_ext}
%endfor

PYBIND11_MODULE(${summary.ref}, m) {

    // Module long description
    m.doc() = ${summary.long_desc};

    // Import modules this extension depends on
    %for ipd in summary.inter_package_dependencies:
    py::module_::import("${ipd}");
    %endfor

    // Call binding functions
    %for header in summary.unit_headers:
    init_${header| cf.filename_no_ext}(m);
    %endfor

}

</%block>
