import os
import json
import subprocess
from typing import Optional


def load_and_save_cfg_help() -> None:
    cfg_help_dict = {}
    if not "doxy_help.json" in dir(os.getcwd()):
        subprocess.run([
            "doxygen",
            "-g",
            "doxy_cfg_help"
            ])
        with open("doxy_cfg_help", "r") as doxy_help:
            field_comment = ""
            cmt_header = False
            for line in doxy_help.readlines():

                # Skip config headers
                if line.startswith("#-"):
                    if cmt_header:
                        cmt_header = False
                    else:
                        cmt_header = True

                if cmt_header:
                    continue

                if line.startswith('#') and not cmt_header:
                    line = line.lstrip('#').lstrip()
                    field_comment += (line + '\n')
                elif '=' in line:
                    cfg_key = line.split('=').rstrip()
                    cfg_help_dict[cfg_key.lower()] = field_comment
                    field_comment = ""
                else:
                    continue

        with open("doxy_help.json", 'w') as dxyhelp:
            dxyhelp.write(json.dumps(cfg_help_dict))
    return


load_and_save_cfg_help()
cfg_help_map = {}
with open("doxy_help.json", "r") as rd_file:
    cfg_help_map = json.loads(rd_file.read())



class DoxyConfig(object):

    cfg_help = cfg_help_map
    def __init__(self):
        self.doxyfile_encoding = "UTF-8"
        self.project_name = "My Project"
        self.project_number = None
        self.project_brief = ""
        self.project_logo = None
        self.output_directory = None
        self.create_subdirs = False
        self.allow_unicode_names = False
        self.output_language = "English"
        self.brief_member_desc = True
        self.repeat_brief = True

        abbrev_brief = r"""
        The $name class \
        The $name widget \
        The $name file \
        is \
        provides \
        specifies \
        contains \
        represents \
        a \
        an \
        the \
        """

        self.abbreviate_brief = abbrev_brief
        self.always_detailed_sec = False
        self.inline_inherited_memb = False
        self.full_path_names = True
        self.strip_from_path = None
        self.strip_from_inc_path = None
        self.short_names = False
        self.javadoc_autobrief = False
        self.qt_autobrief = False
        self.multiline_cpp_is_brief = False
        self.inherit_docs = True
        self.separate_member_pages = False
        self.tab_size = 4
        self.aliases = 'rst="\verbatim embed:rst"'
        self.aliases += 'endrst="\endverbatim"'
        self.aliases += 'inlinerst="\verbatim embed:rst:inline"'
        self.tcl_subst = None
        self.optimize_output_for_c = False
        self.optimize_output_java = False
        self.optimize_for_fortran = False
        self.optimize_output_vhdl = False
        self.extension_mapping = None
        self.markdown_support = True
        self.toc_include_headings = 4
        self.autolink_support = True
        self.builtin_stl_support = False
        self.cpp_cli_support = False
        self.sip_support = False
        self.idl_property_support = True
        self.distribute_group_doc = False
        self.group_nested_compounds = False
        self.subgrouping = True
        self.inline_grouped_classes = False
        self.inline_simple_structs = False
        self.typedef_hides_struct = False
        self.lookup_cache_size = 0
        self.extract_all = False
        self.extract_private = False
        self.extract_package = False
        self.extract_static = False
        self.extract_local_classes = True
        self.extract_local_methods = False
        self.extract_anon_nspaces = False
        self.hide_undoc_members = False
        self.hide_undoc_classes = False
        self.hide_friend_compounds = False
        self.hide_in_body_docs = False
        self.internal_docs = False
        self.case_sense_names = False
        self.hide_scope_names = False
        self.hide_compound_reference = False
        self.show_include_files = True
        self.show_grouped_memb_inc = False
        self.force_local_includes = False
        self.inline_info = True
        self.sort_member_docs = True
        self.sort_brief_docs = False
        self.sort_members_ctors_1st = False
        self.sort_group_names = False
        self.sort_by_scope_name = False
        self.strict_proto_matching = False
        self.generate_todolist = True
        self.generate_testlist = True
        self.generate_buglist = True
        self.generate_deprecatedlist = True
        self.enabled_sections = None
        self.max_initializer_lines = 30
        self.show_used_files = True
        self.show_files = True
        self.show_namespaces = True
        self.file_version_filter = None
        self.layout_file = None
        self.cite_bib_files = None
        self.quiet = False
        self.warnings = True
        self.warn_if_documented = True
        self.warn_if_doc_error = True
        self.warn_no_paramdoc = False
        self.warn_as_error = False
        self.warn_format = "$file:$line: $text"
        self.warn_logfile = None
        self.input = None
        self.input_encoding = "UTF-8"

        file_patterns = r"""
        *.c \
        *.cc \
        *.cxx \
        *.cpp \
        *.c++ \
        *.java \
        *.ii \
        *.ixx \
        *.ipp \
        *.i++ \
        *.inl \
        *.idl \
        *.ddl \
        *.odl \
        *.h \
        *.hh \
        *.hxx \
        *.hpp \
        *.h++ \
        *.cs \
        *.d \
        *.php \
        *.php4 \
        *.php5 \
        *.phtml \
        *.inc \
        *.m \
        *.markdown \
        *.md \
        *.mm \
        *.dox \
        *.py \
        *.pyw \
        *.f90 \
        *.f95 \
        *.f03 \
        *.f08 \
        *.f \
        *.for \
        *.tcl \
        *.vhd \
        *.vhdl \
        *.ucf \
        *.qsf \
        """

        self.file_patterns = file_patterns
        self.recursive = False
        self.exclude = None
        self.exclude_symlinks = False
        self.exclude_patterns = False
        self.exclude_symbols = None
        self.example_path = None
        self.example_patterns = "*"
        self.example_recursive = False
        self.image_path = None
        self.input_filter = None
        self.filter_patterns = None
        self.filter_source_files = False
        self.filter_source_patterns = None
        self.use_mdfile_as_mainpage = None
        self.source_browser = False
        self.inline_sources = False
        self.strip_code_comments = True
        self.referenced_by_relation = False
        self.references_relation = False
        self.references_link_source = True
        self.source_tooltips = True
        self.use_htags = False
        self.verbatim_headers = True
        self.clang_assisted_parsing = False
        self.clang_options = None
        self.alphabetical_index = True
        self.cols_in_alpha_index = 5
        self.ignore_prefix = None
        self.generate_html = False
        self.html_output = "html"
        self.html_file_extension = ".html"
        self.html_header = None
        self.html_footer = None
        self.html_stylesheet = None
        self.html_extra_stylesheet = None
        self.html_extra_files = None
        self.html_colorstype_hue = 220
        self.html_colorstyle_sat = 100
        self.html_colorstyle_gamma = 80
        self.html_timestamp = False
        self.html_dynamic_sections = False
        self.html_index_num_entries = 100
        self.generate_docset = False
        self.docset_feedname = "Doxygen generated docs"
        self.docset_bundle_id = "org.doxygen.Project"
        self.docset_publisher_id = "org.doxygen.Publisher"
        self.docset_publisher_name = "Publisher"
        self.generate_htmlhelp = False
        self.chm_file = None
        self.hhc_location = None
        self.generate_chi = False
        self.chm_index_encoding = None
        self.binary_toc = False
        self.toc_expand = False
        self.generate_qhp = False
        self.qch_file = None
        self.qhp_namespace = "org.doxygen.Project"
        self.qhp_virtual_folder = "doc"
        self.qhp_cust_filter_name = None
        self.qhp_cust_filter_attrs = None
        self.qhp_sect_filter_attrs = None
        self.qhg_location = None
        self.generate_eclipsehelp = False
        self.eclipse_doc_id = "org.doxygen.Project"
        self.disable_index = False
        self.generate_treeview = False
        self.enum_values_per_line = 4
        self.treeview_width = 250
        self.ext_links_in_window = False
        self.formula_fontsize = 10
        self.formula_transparent = True
        self.use_mathjax = False
        self.mathjax_format = "HTML-CSS"
        self.mathjax_relpath = "http://cdn.mathjax.org/mathjax/latest"
        self.mathjax_extensions = None
        self.mathjax_codefile = None
        self.searchengine = True
        self.server_based_search = False
        self.external_search = False
        self.searchengine_url = None
        self.searchdata_file = "searchdata.xml"
        self.external_search_id = None
        self.extra_search_mappings = None
        self.generate_latex = False
        self.latex_output = "latex"
        self.latex_cmd_name = "latex"
        self.makeindex_cmd_name = "makeindex"
        self.compact_latex = False
        self.paper_type = "a4"
        self.extra_packages = None
        self.latex_header = None
        self.latex_footer = None
        self.latex_extra_stylesheet = None
        self.latex_extra_files = None
        self.pdf_hyperlinks = True
        self.use_pdflatex = True
        self.latex_batchmode = False
        self.latex_hide_indices = False
        self.latex_source_code = False
        self.latex_bib_style = "plain"
        self.latex_timestamp = False
        self.generate_rtf = False
        self.rtf_output = "rtf"
        self.compact_rtf = False
        self.rtf_hyperlinks = False
        self.rtf_stylesheet_file = None
        self.rtf_extensions_file = None
        self.rtf_source_code = False
        self.generate_man = False
        self.man_output = "man"
        self.man_extension = ".3"
        self.man_subdir = None
        self.man_links = False
        self.generate_xml = True
        self.xml_output = "xml"
        self.xml_programlisting = True
        self.generate_docbook = False
        self.docbook_output = "docbook"
        self.docbook_programlisting = False
        self.generate_autogen_def = False
        self.generate_perlmod = False
        self.perlmod_latex = False
        self.perlmod_pretty = True
        self.perlmod_makevar_prefix = None
        self.enable_preprocessing = True
        self.macro_expansion = False
        self.expand_only_predef = False
        self.search_includes = True
        self.include_path = None
        self.include_file_patterns = None
        self.predefined = None
        self.expand_as_defined = None
        self.skip_function_macros = True
        self.tagfiles = None
        self.generate_tagfile = False
        self.allexternals = False
        self.external_groups = True
        self.external_pages = True
        self.perl_path = "/usr/bin/perl"
        self.class_diagrams = True
        self.mscgen_path = None
        self.dia_path = None
        self.hide_undoc_relations = True
        self.have_dot = True
        self.dot_num_threads = 0
        self.dot_fontname = "Helvetica"
        self.dot_fontsize = 10
        self.dot_fontpath = None
        self.class_graph = True
        self.collaboration_graph = True
        self.group_graphs = True
        self.uml_look = False
        self.uml_limit_num_fields = 10
        self.template_relations = False
        self.include_graph = True
        self.included_by_graph = True
        self.call_graph = False
        self.caller_graph = False
        self.graphical_hierarchy = True
        self.directory_graph = True
        self.dot_image_format = "png"
        self.interactive_svg = False
        self.dot_path = None
        self.dotfile_dirs = None
        self.mscfile_dirs = None
        self.diafile_dirs = None
        self.plantuml_jar_path = None
        self.plantuml_cfg_file = None
        self.plantuml_include_path = None
        self.dot_graph_max_nodes = 50
        self.max_dot_graph_depth = 0
        self.dot_transparent = False
        self.dot_multi_targets = False
        self.generate_legend = True
        self.dot_cleanup = True

        self.doxy_cfg = ""
        return

    def doxy_help(key: Optional[str]) -> None:
        if key is None:
            for key, item in DoxyConfig.cfg_help_map.items():
                print(key + "\n")
                print(item)
                print()
            return

        print(key + '\n') 
        print(DoxyConfig.cfg_help_map[key])
        print()
        return
    
    def write_doxy_cfg(self, cfg_file: str) -> None:
        self.doxy_cfg = os.path.abspath(cfg_file)
        out_str = ""
        for cfg_field in vars(self):
            key = cfg_field.upper()
            val = getattr(self, cfg_field)
            if val is None:
                val = ""
            elif val == True:
                val = "YES"
            elif val == False:
                val = "NO"
            val = str(val)
            out += f"{key} = {val}"
            out += "\n"
        with open(cfg_file, "w") as cfg_out:
            cfg_out.write(out_str)
        return

    def delete_doxy_cfg(self) -> None:
        if os.path.exists(self.doxy_cfg):
            os.remove(self.doxy_cfg)
        return

