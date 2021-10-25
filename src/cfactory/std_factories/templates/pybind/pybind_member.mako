<%!
    import illuminate.std_factories.file_formatter as ff
    import illuminate.std_factories.common_filters as cf
    import illuminate.std_factories.mako_global as mg
    from illuminate.code_models.union import UnionObject
    from clang import cindex
%>
<%page args="mo"/>
<%namespace name="union" file="union.mako"/>

<%
    cls_name = mg.class_ids[mo.scope.qualified_id]
%>


<%def name="write_class_member(cls_mem)" filter="trim">
%if int(cls_mem.access_specifier.value) == int(cindex.AccessSpecifier.PUBLIC.value):
%if cls_mem.storage_class is cindex.StorageClass.STATIC and not cls_mem.constness:
${cls_name}.def_readwrite_static("${cls_mem.pyname}", &${cls_mem.qualified_id}) \
%elif cls_mem.storage_class is cindex.StorageClass.STATIC:
${cls_name}.def_readonly_static("${cls_mem.pyname}", &${cls_mem.qualified_id}) \
%elif cls_mem.constness:
${cls_name}.def_readonly("${cls_mem.pyname}", &${cls_mem.qualified_id}) \
%elif isinstance(cls_mem, UnionObject):
${cls_name}.def_property_readonly("${cls_mem.pyname}", ${union.union_member_property(cls_mem)}) \
%else:
${cls_name}.def_readwrite("${cls_mem.id}", &${cls_mem.qualified_id}) \
%endif
%endif
</%def>

<%def name="write_class_property(prop, get, set)" filter="trim">
%if prop.storage_class is cindex.StorageClass.STATIC and not prop.constness and set is not None:
${cls_name}.def_property_static("${prop}", &${get.qualified_id}, &${set.qualified_id}) \
%elif prop.storage_class is cindex.StorageClass.STATIC and get is not None:
${cls_name}.def_property_readonly_static("${prop}", &${get.qualified_id}) \
%elif prop.constness and get is not None:
${cls_name}.def_property_readonly("${prop}", &${get.qualified_id}) \
%else:
%if get is not None and set is not None:
${cls_name}.def_property("${prop}", &${get.qualified_id}, &${set.qualified_id}) \
%endif
%endif
</%def>

${capture(write_class_member, mo)|trim}
