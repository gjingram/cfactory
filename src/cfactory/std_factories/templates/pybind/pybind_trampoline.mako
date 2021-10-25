<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
    from illuminate.code_models.class_object import ClassObject

    trampoline_name = ""
    template_param = ""
    pure_virtuals = []
    virtuals = []
    inherits_from = ""
%>

<%page args="cls, module_instance" expression_filter="trim"/>
<%namespace name="utils" file="util_defs.mako"/>

<%
    def trampoline_init(cls: ClassObject) -> None:
        global trampoline_name = ""
        global template_param = ""
        global pure_virtuals = []
        global virtuals = []
        global inherits_from = ""

	trampoline_name = "Py" + cls.pyname
	mg.trampoline_classes[cls.qualified_id] = trampoline_name

	template_param = cls.pyname + "Base"
	is_trampoline_base = cls.pybind.py_inheritable_base

	if is_trampoline_base:
            mg.trampoline_bases[cls.qualified_id] = trampoline_name

	pure_virtuals = [(method, False) for method in cls.functions if method.is_pure_virtual]
	virtuals = [(method, False) for method in cls.functions if method.is_virtual]

	def set_update_flag(method_pairs, method_name):
	    for pair in method_pairs:
		if pair[0] == method_name:
	            pair[1] = True
	    return

	if bool(len(cls.pybind.limit_py_inherited_to)):
            pure_virtuals = [pair for pair in pure_virtuals if pair[0] \
		in cls.pybind.limit_py_inherited_to]
	    virtuals = [pair for pair in virtuals if pair[0] in \
		cls.pybind.limit_py_inherited_to]

	pure_virtual_names = [pair[0] for pair in pure_virtuals]
	virtual_names = [pair[0] for pair in virtuals]

	trampoline_base = None
	for parent_class in cls.get_parent_objects():
            if parent_class.qualified_id not in mg.trampoline_bases:
		continue
	    trampoline_base = mg.trampoline_bases[parent_class.qualified_id]
	    for parent_method in parent_class.functions:
		if parent_method.pyname in pure_virtual_names and \
		    not parent_method.is_pure_virtual:
		    set_update_flag(pure_virtuals, parent_method.pyname)
		if parent_method.pyname in virtual_names and not parent_method.is_virtual:
		    set_update_flag(virtuals, parent_method.pyname)
	    break

	inherits_from = template_param if trampoline_base is None else \
	    f"{trampoline_base}<{template_param}>"
%>

<%def name="trampoline_override(method, pure_virtual)" filter="trim">
${method.return_type} \
${method.id}(\
${capture(utils.str_list, [x.type + x.id for x in method.info['args'].values()])| trim, cf.plfsl, cf.stc})\
%if method.is_const:
 const \
%endif
 override { \
%if pure_virtual:
PYBIND11_OVERRIDE_PURE(\
%else:
PYBIND11_OVERRIDE(\
%endif
${method.return_type}, \
${cls.pyname + "Base"}, \
${method.pyname}, \
%if bool(len(method.info['args'])):
${capture(utils.str_list, [x.id for x in method.info['args'].values()])| trim, cf.plfsl, cf.stc}\
); \
}
</%def>

<%def name="write_trampoline_class(cls)" filter="trim">
<%
    trampoline_init(cls)
%>
template <class ${template_param} = ${cls.qualified_id}>
class ${trampoline_name} : public ${inherits_from} {
    
    public:
    using ${inherits_from}::${inherits_from};
    %for pv in pure_virtuals:
    %if pv[1]:
    ${trampoline_override(pv[0], True)| trim}
    %endif
    %endfor
    %for v in virtuals:
    %if v[1]:
    ${trampoline_override(v[0], False)| trim}
    %endif
    %endfor

};
<%/def>

${write_trampoline_class}
        
