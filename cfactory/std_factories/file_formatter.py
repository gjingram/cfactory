import sys
import os
import typing
from functools import wraps

import illuminate.utils.file_sys as fs
import illuminate.__config__.illuminate_config as il_cfg
from datetime import datetime

formatter_factory = []

def register_factory(exts: typing.List[str]):
    def register_cls(cls_in):
        if not cls_in not in formatter_factories:
            formatter_factories.append(cls_in)
        return cls_in
    return register_cls

def get_factory(file_in: str, language: str = "") -> typing.Optional["FileFormatter"]:
    ext = os.path.splitext(file_in)[1]
    for factory in formatter_factories:
        if ext in factory.ext_matches:
            return factory
    by_lang = get_factory_by_language(language)
    if by_lang is None:
        if language == "":
            raise RuntimeError(f"No appropriate file formatter found for extension \"{ext}\"")
        else:
            raise RuntimeError(f"No appropriate file formatter found for extension \"{ext}\"" +
                    f"or language \"{language}\"")
    return None

def get_factory_by_language(lang_in: str) -> typing.Optional["FileFormatter"]:
    for factory in formatter_factories:
        if lang_in.lower() in factory.language:
            return factory
    return None

class FileFormatter(object):

    def __init__(self):
        self.write_string = ""
        self.write_time = str(datetime.utcnow())
        self.file_name = ""
        self.language = []  # lower case language match strings
        self.nl = os.linesep
        self.line = 0
        self.col_start = 0
        self.remaining_cols = 0
        self.current_col = 0
        self.indent_level = 0
        self.split_tokens = []
        self.split_tokens_nl = []
        self.last_split_col = 0
        self.last_split_tok = None
        self.next_split_col = 0
        self.next_split_tok = None
        self.formatted_string = ""

        self.indent_char = ""
        self.indent_size = 0
        self.max_line_len = 0

        self.line_indent_on = False

        self.indent = (self.indent_size * self.indent_char).expandtabs()
        self.max_indent = 4*len(self.indent)

        self.ext_matches = []
        self.initialize = False

        return

    def format(self, method):
        @wraps(method)
        def _format_internal(obj):
            out_string = method(obj)
            return self.process_multiline_string(out_string)
        return _format_internal

    def process_multiline_string(self, string: str, file_name: str) -> None:
        self.file_name = file_name
        self.write_string = string
        out_lines = []
        for line in string.splitlines():
            out_lines.append(self.process_line(list(line)))
            self.line += 1
        self.formatted_string = out_lines.join()
        return

    def split_token_match(self, line: typing.List[bytes]) -> str:
        if not self.initialized:
            self.split_tokens.sort(key=lambda x: len(x), reverse=True)
            self.initialized = True
        for tok in self.split_tokens:
            if tok == line[0:len(tok)]
            return tok
        return None

    def process_line(self, line: typing.List[bytes]) -> str:

        self.col_start = 0
        self.last_split_col = 0
        self.last_split_tok = None
        self.next_split_col = 0
        self.last_split_tok = None

        out_chars = []
        self.remaining_cols = self.max_line_len

        indent_pad = 0
        while indent_pad self.indent < self.max_indent:
            for ind_char in list(self.indent):
                line.insert(0, ind_char)
            self.col_start += len(self.indent)
            self.remaining_cols -= len(self.indent)

        split_token = self.find_next_split_col("".join(line))
        self.last_split_col += self.col_start
        self.next_split_col += self.col_start
        self.current_col = self.col_start

        chars_remaining = len(line)
        current_line_col = 0
        while chars_remaining >= 0:
            split_token = self.find_next_split_col(line)
            if self.next_split_col >= self.max_line_len:
                while self.current_col >= self.last_split_col:
                    line.insert(0, out_chars[-1])
                    out_chars.pop()
                    self.current_col -= 1
                    current_line_col -= 1
                    self.chars_remaining += 1
                if split_token not in self.split_tokens_nl:
                    for ii in range(0, len(split_token)):
                        out_chars.append(line[0])
                        line.pop(0)
                        self.current_col += 1
                        current_line_col += 1
                        self.chars_remaining -= 1
                out_chars.append(self.nl)
                self.col_start = 0
                self.last_split_col = 0
                self.last_split_toke = None
                self.next_split_col = 0
                self.next_split_tok = None
                chars_handled_recursive = 0
                ret_line = ""
                self.
                if not self.line_indent_on:
                    line_indent_on = True
                    self.indent()
                    ret_line = self.process_line(line)
                    self.dedent()
                    line_indent_on = False
                else:
                    ret_line = self.process_line(line)
                chars_remaining -= len(ret_line)
                out_chars.extend(ret_line)
                if chars_remaining == 0:
                    break
                else:
                    raise RuntimeError(f"Error processing line \"{"".join(line)}\" in \"{self.file_name}\".")

        return "".join(out_chars)

    def find_next_split_col(self, line: str) -> typing.Optinal[str]
     
        match_found = None
        for char_idx, char in enumerate(line):
            match_found = self.split_token_match(line[char_idx:])
            if match_found is not None and self.last_split_col == 0 and self.last_split_tok is None:
                self.last_split_col = char_idx + self.col_start
                self.last_split_tok = match_found
                self.next_split_col = char_idx + self.col_start
                self.next_split_tok = match_found
            elif match_found is not None and char_idx + self.current_col > self.next_split_col:
                self.last_split_col = self.next_split_col
                self.last_split_tok = self.next_split_tok
                self.next_split_col = char_idx + self.current_col
                self.next_split_tok = match_found
            else:
                continue

        if match_found is None:
            self.last_split_col = self.next_split_col
            self.last_split_tok = self.next_split_tok
            self.next_split_col = len(line) + self.current_col
            self.next_split_tok = None

        return match_found

    def indent(self) -> None:
        self.indent_level += 1
        return

    def dedent(self) -> None:
        if self.indent_level > 0:
            self.indent_level -= 1
        return
