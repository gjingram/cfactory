<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
    import pdb
%>

<%page args="union, module_instance" expression_filter="trim"/>
<%namespace name="utils" file="util_defs.mako"/>
<%namespace name="lambda" file="lambda.mako"/>

<%def name="union_member_property(union_in)" filter="trim"/>
[wrap=UnionWrap_${union.pyname}()](${union_in.scope.qualified_id} const &cls) -> UnionWrap_${union_in.pyname} & {
    if (wrap._data == NULL) {
        wrap._data = reinterpret_cast<void *>(&(cls.${union_in.id}));
    }
    return wrap;
}
</%def>


<%def name="write_union_properties(union_in)" filter="trim"/>
    for field_name in union_in.fields.keys():
    .def_property(${field.pyname}, &UnionWrap_${union.pyname}::${field.pyname}_get, &${union_in.qualified_id}::${field.pyname}_set)\
    %endfor
</%def>

struct UnionWrap_${union.pyname} {

    void *_data = NULL;
    %for field in union.fields.values():
    auto ${field.pyname}_get = ${lambda.union_casting_getter("UnionWrap_${union.pyname}", "_data", ${field.type})};

    auto ${field.pyname}_set = ${lambda.union_casting_setter("UnionWrap_${union.pyname}", "_data", ${field.type})};
    
    %endfor\
};

py::class_(${module_instance}, "${union.pyname}")
    ${write_union_properties(union)}\
    ;
    
