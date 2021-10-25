<%!
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    import illuminate.std_factories.check_pybind as cp
    import pdb
    from clang import cindex
%>

<%page args ="cls, module_instance" expression_filter="trim"/>
<%namespace name="utils" file="util_defs.mako"/>
<%namespace name="members" file="member.mako"/>
<%namespace name="mfunctions" file="member_function.mako"/>
<%namespace name="enum" file="enum.mako"/>
<%namespace name="trampoline" file="trampoline.mako"/>


<%

    instance_name = '_'+ cls.pyname.lower()
    mg.class_ids[cls.qualified_id] = instance_name

    def _arg_name(object):
        print(object.get_name())
        return object

    for class_obj in cls.all_objects:
        print(class_obj.get_name() + ' loop')
        cp.check_pybind_opt(_arg_name(class_obj))

    property_map = {}
    for mfunc in cls.functions:
        if mfunc.pybind.property_getter or mfunc.pybind.property_setter:
            assert mfunc.pybind.property_refers_to is not None
            
            if not mfunc.pybind.property_refers_to in property_map:
                property_map[property_name] = {
                                               reference: mfunc.pybind.property_refers_to,
                                               getter: None,
                                               setter: None
                                              }
                if mfunc.pybind.property_getter:
                    property_map[property_name]['getter'] = \
                        mfunc

                if mfunc.pybind.property_setter:
                    property_map[property_name]['setter'] = \
                        mfunc

    def method_check(method_in) -> bool:
        return not method.is_pure_virtual or method.id in trampoline.pure_virtuals

%>

<%def name="write_class_args(cls_in)" decorator="cp.check_opt" filter="trim">
${module_instance} \
"${cls_in.pyname}" \
%if cls_in.pybind.py_extendable:
py::dynamic_attr() \
%endif
%if cls_in.pybind.module_local:
py::module_local() \
%endif
%if cls_in.pybind.is_final:
py::is_final() \
%endif
</%def>

<%def name="write_cls_template_args(cls_in)" decorator="cp.check_opt" filter="trim">
${cls_in.pyname} \
%for parent in [p for p in cls_in.class_parent_types if p in mg.class_ids]:
${parent} \
%endfor
%if cls_in.pybind.py_inheritable:
%if cls_in.qualified_id in mg.trampoline_bases:
${trampoline.trampoline_name + "<>"} \
%elif cls_in.qualified_id in mg.trampoline_classes:
${trampoline.trampoline_name + f"<{cls_in.qualified_id}>"} \
%endif
</%def>

<%def name="write_class(cls_in)" decorator="cp.check_opt" filter="trim">
%if cls_in.pybind.py_inheritable:
${trampoline.write_trampoline_class(cls_in)|trim}
%endif
%for cls_internal in cls_in.classes:
${write_class(cls_internal)}
%endfor
%for struct_internal in cls_in.structs:
${write_class(struct_internal)}
%endfor
/* ${cls_in.header.header_relpath}:${cls_in.qualified_id} */
${cls.pybind.pybind_class_obj}<\
${capture(write_cls_template_args, cls_in)| trim, cf.plfsl, cf.stc}> \
${instance_name}\
(\
${capture(write_class_args, cls_in)| trim, cf.plfsl, cf.stc}\
);

// ${cls.qualified_id} class constructors
%for ctor in cls.class_constructors:
%if method_check(ctor):
${instance_name}.${mfunctions.write_ctor(ctor)};
%endif
%endfor

// ${cls.qualified_id} factory methods
%for factory in [ffunc for ffunc in cls.functions if ffunc.pybind.factory_method]:
%if method_check(factory):
${instance_name}.def(py::init(&${ffunc.qualified_id});
%endif
%endfor

// ${cls.qualified_id} magic methods
%for mm in [ffunc for ffunc in cls.functions if ffunc.magic]:
%if method_check(mm):
${instance_name}.${mfunctions.write_magic_method(mm)};
%endif
%endfor

// ${cls.qualified_id} public methods
%for rm in [ffunc for ffunc in cls.functions if not ffunc.magic and \
    not ffunc.is_ctor and not ffunc.is_conversion and not ffunc.is_dtor \
    and ffunc.access_specifier.value == cindex.AccessSpecifier.PUBLIC.value \
    and not (ffunc.pybind.property_getter or ffunc.pybind.property_setter)]:
%if method_check(rm):
${instance_name}.${mfunctions.write_method(rm)};
%endif
%endfor

// ${cls.qualified_id} public members
%for member in [mem for mem in cls.variables if \
    mem.access_specifier.value == cindex.AccessSpecifier.PUBLIC.value]:
%if method_check(member):
${instance_name}.${members.write_class_member(member)};
%endif
%endfor

// ${cls.qualified_id} properties
%for prop in property_map:
<%
    ref = property_map[prop]["reference"]
    getter = property_map[prop]["getter"]
    setter = property_map[prop]["setter"]
%>
${instance_name}.${members.write_class_property(ref, getter, setter)};
%endfor

// ${cls.qualified_id} enums
%for cls_enum in cls.enumerations:
${enum.write_enum(cls_enum, instance_name)};
%endfor

// ${cls.qualified_id} implicit conversions
%for convf in [fn for fn in cls.functions if fn.is_conversion]:
${instance_name}.${mfunctions.write_conversion(convf)};
%endfor
</%def>

${write_class(cls)}
