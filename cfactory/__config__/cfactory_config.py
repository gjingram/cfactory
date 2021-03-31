import sys
import pathlib
import os
from loguru import logger
from warnings import warn

cfactory_top = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parents[0])

def log_parsed_objects(record):
    return record["extra"]["log_parsed"] and record["extra"]["logs_parses"]

def log_object_dependencies(record):
    return record["extra"]["log_object_deps"] and record["extra"]["logs_object_deps"]

def log_module_dependencies(record):
    return record["extra"]["log_module_deps"] and record["extra"]["logs_module_deps"]

def log_package_dependencies(record):
    return record["extra"]["log_package_deps"] and record["extra"]["logs_package_deps"]

def cfactory_stage_log(record):
    return record["extra"]["stage_log"]

cfactory_stage_fmt = "CFactory: {message}"
cfactory_common_fmt = "CFactory: {extra[project]}:{extra[package]}:{extra[header]} -- {message}"

class IndentingParseFormatter(object):

    def __init__(self):
        self.n_spaces = 3
        self.indent_level = 0
        self.fmt = "CFactory: {extra[header]} -- " + "{extra[indent]}++{message}\n"
        return

    def format(self, record):
        record["extra"]["indent"] = self.indent_level * self.n_spaces * " "
        return self.fmt

indenting_formatter = IndentingParseFormatter()

cf_log_config = {
        "handlers": [
            {"sink": sys.stdout, "format": cfactory_stage_fmt, "filter": cfactory_stage_log},
            {"sink": sys.stdout, "format": indenting_formatter.format, "filter": log_parsed_objects},
            {"sink": sys.stdout, "format": indenting_formatter.format, "filter": log_object_dependencies},
            {"sink": sys.stdout, "format": cfactory_common_fmt, "filter": log_module_dependencies},
            {"sink": sys.stdout, "format": cfactory_stage_fmt, "filter": log_package_dependencies}
            ],
        "extra": {
            "project": "",
            "package": "",
            "header": "",
            "indent": "",
            "log_parsed": False,
            "logs_parses": False,
            "log_object_deps": False,
            "logs_object_deps": False,
            "log_module_deps": False,
            "logs_module_deps": False,
            "log_package_deps": False,
            "logs_package_deps": False,
            "stage_log": False
            }
        }

logger.configure(**cf_log_config)
logger.disable("cfactory")

object_registry = []

logger_registry = {}

project = ""
package = ""
log_parsed = False
log_object_deps = False
log_module_deps = False
log_package_deps = False

pkg_logger = None

c_indent_char = " "
c_indent_size = 4
c_max_line_len = 80
c_src_ext = ".c"
c_header_ext = ".h"

cpp_indent_char = " "
cpp_indent_size = 4
cpp_max_line_len = 80
cpp_src_ext = ".cpp"
cpp_header_ext = ".hh"
cpp_template_ext = ".tpp"

py_indent_char = " "
py_indent_size = 4
py_max_line_len = 80
py_src_ext = ".py"

js_indent_char = " "
js_indent_size = 4
js_max_line_len = 80
js_src_ext = ".js"

suppress_c_format_warnings = False
suppress_cpp_format_warnings = False
suppress_py_format_warnings = False
suppress_js_format_warnings = False

def set_c_indent_char(ind_char: str) -> None:
    global c_indent_char
    if not ind_char in [" ", "\t"] and not suppress_c_format_warnings:
        warn(fr"Non-standard C indent character \"{ind_char}\" specified.")
    c_indent_char = ind_char
    return

def set_c_indent_size(ind_size: int) -> None:
    global c_indent_size
    c_indent_size = ind_size
    return

def set_c_max_line_len(line_len: int) -> None:
    global c_max_line_len
    c_max_line_len = line_len
    return

def set_c_src_ext(ext: str) -> None:
    global c_src_ext
    if ext != ".c" and not suppress_c_format_warnings:
        warn(f"Non-standard C source extension \"{ext}\" specified.")
    c_src_ext = ext
    return

def set_c_header_ext(ext: str) -> None:
    global c_header_ext
    if ext != ".h" and not suppress_c_format_warnings:
        warn(f"Non-standard C header extension \"{ext}\" specified.")
    c_header_ext = ext
    return

def set_cpp_indent_char(ind_char: str) -> None:
    global cpp_indent_char
    if not ind_char in [" ", "\t"] and not suppress_cpp_format_warnings:
        warn(fr"Non-standard C++ indent character \"{ind_char}\" specified.")
    cpp_indent_char = ind_char
    return

def set_cpp_indent_size(ind_size: int) -> None:
    global cpp_indent_size
    cpp_indent_size = ind_size
    return

def set_cpp_max_line_len(line_len: int) -> None:
    global cpp_max_line_len
    cpp_max_line_len = line_len
    return

def set_cpp_src_ext(ext: str) -> None:
    global cpp_src_ext
    if ext not in [".c", ".cc", ".cpp"] and not suppress_cpp_format_warnings:
        warn(f"Non-standard C++ source extension \"{ext}\" specified.")
    cpp_src_ext = ext
    return

def set_cpp_header_ext(ext: str) -> None:
    global cpp_header_ext
    if ext not in [".h", ".hh", ".hpp"] and not suppress_cpp_format_warnings:
        warn(f"Non-standard C++ header extension \"{ext}\" specified.")
    cpp_header_ext = ext
    return

def set_cpp_template_ext(ext: str) -> None:
    global cpp_template_ext
    cpp_template_ext = ext
    return

def set_py_indent_char(ind_char: str) -> None:
    global py_indent_char
    if ind_char not in [" ", "\t"] and not suppress_py_format_warnings:
        warn(fr"Non-standard python indent character \"{ind_char}\" specified.")
    py_indent_char = ind_char
    return

def set_py_indent_size(ind_size: int) -> None:
    global py_indent_size
    py_indent_size = ind_size
    return

def set_py_max_line_len(line_len: int) -> None:
    global py_max_line_len
    py_max_line_len = line_len
    return

def set_py_source_ext(ext: str) -> None:
    global py_src_ext
    if ext != ".py" and not suppress_py_format_warnings:
        warn(f"Non-standard python source extension \"{ext}\" specified.")
    py_src_ext = ext
    return

def set_js_indent_char(ind_char: str) -> None:
    global js_indent_char
    if ind_char not in [" ", "\t"] and not suppress_js_format_warnings:
        warn(fr"Non-standard javascript indent character \"{ind_char}\" specificed.")
    js_indent_char = ind_char
    return

def set_js_indent_size(ind_size: int) -> None:
    global js_indent_size
    js_indent_size = ind_size
    return

def set_js_max_line_len(line_len: int) -> None:
    global js_max_line_len
    js_max_line_len = line_len
    return

def set_js_source_ext(ext: str) -> None:
    global js_source_ext
    if ext not in [".js", ".jsm"] and not suppress_js_format_warnings:
        warn(f"Non-standard javascript source extension \"{ext}\" specified.")
    js_source_ext = ext
    return

class FormatterConfig(object):

    def __init__(self):
        
        self._c_indent_char = c_indent_char
        self._c_indent_size = c_indent_size
        self._c_max_line_len = c_max_line_len
        self._c_src_ext = c_src_ext
        self._c_header_ext = c_header_ext

        self._cpp_indent_char = cpp_indent_char
        self._cpp_indent_size = cpp_indent_size
        self._cpp_max_line_len = cpp_max_line_len
        self._cpp_src_ext = cpp_src_ext
        self._cpp_header_ext = cpp_header_ext
        self._cpp_template_ext = cpp_template_ext

        self._py_indent_char = py_indent_char
        self._py_indent_size = py_indent_size
        self._py_max_line_len = py_max_line_len
        self._py_src_ext = py_src_ext

        self._js_indent_char = js_indent_char
        self._js_indent_size = js_indent_size
        self._js_max_line_len = js_max_line_len
        self._js_src_ext = js_src_ext

        self._suppress_c_format_warnings = suppress_c_format_warnings
        self._suppress_cpp_format_warnings = suppress_cpp_format_warnings
        self._suppress_py_format_warnings = suppress_py_format_warnings
        self._suppress_js_format_warnings = suppress_js_format_warnings


        return

    def set_config(self) -> None:
        
        set_c_indent_char(self._c_indent_char)
        set_c_indent_size(self._c_indent_size)
        set_c_max_line_len(self._c_max_line_len)
        set_c_src_ext(self._c_src_ext)
        set_c_header_ext(self._c_header_ext)

        set_cpp_indent_char(self._cpp_indent_char)
        set_cpp_indent_size(self._cpp_indent_size)
        set_cpp_max_line_len(self._cpp_max_line_len)
        set_cpp_src_ext(self._cpp_src_ext)
        set_cpp_header_ext(self._cpp_header_ext)
        set_cpp_template_ext(self._cpp_template_ext)

        set_py_indent_char(self._py_indent_char)
        set_py_indent_size(self._py_indent_size)
        set_py_max_line_len(self._py_max_line_len)
        set_py_src_ext(self._py_src_ext)

        set_js_indent_char(self._js_indent_char)
        set_js_indent_size(self._js_indent_size)
        set_js_max_line_len(self._js_max_line_len)
        set_js_src_ext(self._js_src_ext)

        global suppress_c_format_warnings
        global suppress_cpp_format_warnings
        global suppress_py_format_warnings
        global suppress_js_format_warnings

        suppress_c_format_warnings = self._suppress_c_format_warnings
        suppress_cpp_format_warnings = self._suppress_cpp_format_warnings
        suppress_py_format_warnings = self._suppress_py_format_warnings
        suppress_js_format_warnings = self._suppress_js_format_warnings

        return

    @property
    def c_indent_char(self) -> str:
        return c_indent_char

    @c_indent_char.setter
    def c_indent_char(self, ind_char: str) -> None:
        self._c_indent_char = ind_char
        return None

    @property
    def c_indent_size(self) -> int:
        return c_indent_size

    @c_indent_size.setter
    def c_indent_size(self, ind_size: int) -> None:
        self._c_indent_size = ind_size
        return

    @property
    def c_max_line_len(self) -> int:
        return c_max_line_len

    @c_max_line_len.setter
    def c_max_line_len(self, line_len: int) -> None:
        self._c_max_line_len = line_len
        return

    @property
    def c_src_ext(self) -> str:
        return c_src_ext

    @c_src_ext.setter
    def c_src_ext(self, ext: str) -> None:
        self._c_src_ext = ext
        return

    @property
    def c_header_ext(self) -> str:
        return c_header_ext

    @c_header_ext.setter
    def c_header_ext(self, ext: str) -> None:
        self._c_header_ext = ext

    @property
    def cpp_indent_char(self) -> str:
        return cpp_indent_char

    @cpp_indent_char.setter
    def cpp_indent_char(self, ind_char: str) -> None:
        self._cpp_indent_char = ind_char
        return

    @property
    def cpp_indent_size(self) -> int:
        return cpp_indent_size

    @cpp_indent_size.setter
    def cpp_indent_size(self, ind_size: int) -> None:
        self._cpp_indent_size = ind_size
        return

    @property
    def cpp_max_line_len(self) -> int:
        return cpp_max_line_len

    @cpp_max_line_len.setter
    def cpp_max_line_len(self, line_len: int) -> None:
        self._cpp_max_line_len = line_len
        return

    @property
    def cpp_src_ext(self) -> str:
        return cpp_src_ext

    @cpp_src_ext.setter
    def cpp_src_ext(self, ext: str) -> None:
        self._cpp_src_ext = ext
        return

    @property
    def cpp_header_ext(self) -> str:
        return cpp_header_ext

    @cpp_header_ext.setter
    def cpp_header_ext(self, ext: str) -> None:
        self._cpp_header_ext = ext
        return

    @property
    def cpp_template_ext(self) -> str:
        return cpp_template_ext

    @cpp_template_ext.setter
    def cpp_template_ext(self, ext: str) -> None:
        self._cpp_template_ext = ext
        return

    @property
    def py_indent_char(self) -> str:
        return py_indent_char

    @py_indent_char.setter
    def py_indent_char(self, ind_char: str) -> None:
        self._py_indent_char = ind_char
        return

    @property
    def py_indent_size(self) -> int:
        return py_indent_size

    @py_indent_size.setter
    def py_indent_size(self, ind_size: int) -> None:
        self._py_indent_size = ind_size
        return

    @property
    def py_max_line_len(self) -> int:
        return py_max_line_len

    @py_max_line_len.setter
    def py_max_line_len(self, line_len: int) -> None:
        self._py_max_line_len = line_len
        return

    @property
    def py_src_ext(self) -> str:
        return py_src_ext

    @py_src_ext.setter
    def py_src_ext(self, ext: str) -> None:
        self._py_src_ext = ext
        return

    @property
    def js_indent_char(self) -> str:
        return js_indent_char

    @js_indent_char.setter
    def js_indent_char(self, ind_char: str) -> None:
        self._js_indent_char = ind_char
        return

    @property
    def js_indent_size(self) -> int:
        return js_indent_size

    @js_indent_size.setter
    def js_indent_size(self, ind_size: int) -> None:
        self._js_indent_size = ind_size
        return

    @property
    def js_max_line_len(self) -> int:
        return js_max_line_len

    @js_max_line_len.setter
    def js_max_line_len(self, line_len: int) -> None:
        self._js_max_line_len = line_len
        return

    @property
    def js_src_ext(self) -> str:
        return js_src_ext

    @js_src_ext.setter
    def js_src_ext(self, ext: str) -> None:
        self._js_src_ext = ext
        return

    @property
    def suppress_c_format_warnings(self) -> bool:
        return self._suppress_c_format_warnings

    @suppress_c_format_warnings.setter
    def suppress_c_format_warnings(self, do_it: bool) -> None:
        self._suppress_c_format_warnings = do_it
        return

    @property
    def suppress_cpp_format_warnings(self) -> bool:
        return self._suppress_cpp_format_warnings

    @suppress_cpp_format_warnings.setter
    def suppress_cpp_format_warnings(self, do_it: bool) -> None:
        self._suppress_cpp_format_warnings = do_it
        return

    @property
    def suppress_py_format_warnings(self) -> bool:
        return self._suppress_py_format_warnings

    @suppress_py_format_warnings.setter
    def suppress_py_format_warnings(self, do_it: bool) -> None:
        self._suppress_py_format_warnings = do_it
        return

    @property
    def suppress_js_format_warnings(self) -> bool:
        return self._suppress_js_format_warnings

    @suppress_js_format_warnings.setter
    def suppress_js_format_warnings(self, do_it: bool) -> None:
        self._suppress_js_format_warnings
        return

license_file = ""
