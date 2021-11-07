import os
import sys
import shutil
from typing import Optional

import cfactory.utils.file_writer as fw


class LongCommentStyle(object):
    SPAN_POUND = 0
    NO_PRE_POST = 1
    MULTILINE = 2


class ShortCommentStyle(object):
    POUND = 0

comment_wrappers = {
        "long": {},
        "short": {}
        }

def fmt_span_pound_long_comment(cmt: str, **extras) -> str:
    cmt_lines = cmt.split(os.newline)
    pre_post = extras["max_cols"] * '#' + "\n"
    out = pre_post
    for cmt_line in cmt_lines:
        out += "# " + cmt_line + "\n"
    out += pre_post
    return out

def fmt_no_pre_post_long_comment(cmt: str, **extras) -> str:
    cmt_lines = cmt.split(os.newline)
    out = ""
    for cmt_line in cmt_lines:
        out += "# " + cmt_line + "\n"
    return out

def fmt_multiline_long_comment(cmt: str, **extras) -> str:
    return "'''\n" + cmt + "'''\n"

def fmt_pound_short_comment(cmt: str, **extras) -> str:
    return "# " + cmt + "\n"

comment_wrappers["long"][LongCommentStyle.SPAN_POUND] = (
        fmt_span_pound_long_comment
        )
comment_wrappers["long"][LongCommentStyle.NO_PRE_POST] = (
        fmt_no_pre_post_long_comment
        )
comment_wrappers["long"][LongCommentStyle.MULTILINE] = (
        fmt_multiline_long_comment
        )
comment_wrappers["short"][ShortCommentStyle.POUND] = (
        fmt_pound_short_comment
        )


class PyFileWriter(fw.CodeWriter):

    def __init__(
            self,
            displayname: str,
            path: str,
            license_section: Optional[fw.FileSection] = None,
            license_file: Optional[str] = None,
            license_text: Optional[str] = None,
            footer_section: Optional[fw.FileSection] = None,
            footer_text: Optional[str] = None):
        super().__init__(
                displayname,
                path,
                license_section,
                license_file,
                license_text,
                footer_section,
                footer_text
                )

        self.long_comment_style = LongCommentStyle.MULTILINE
        self.short_comment_style = ShortCommentStyle.POUND
        self.short_comment_wrapper = comment_wrappers["short"][
                self.short_comment_style]

        return

    def initialize_writer(self) -> None:
        self.long_comment_wrapper = comment_wrappers["long"][
                self.long_comment_style]
        self.header.wrap_fn = self.long_comment_wrapper
        self.footer.wrap_fn = self.short_comment_wrapper
        return
