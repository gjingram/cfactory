import os
import sys
import shutil
from typing import Optional

import cfactory.utils.file_writer as fw


class LongCommentStyle(object):
    SPAN_AST = 0
    SHORT_AST = 1
    
class ShortCommentStyle(object):
    SLASH_SLASH = 0
    WRAP_SLASH_SLASH = 1
    WRAP_LONG = 2

comment_wrappers = {
        "long": {},
        "short": {}
        }

def fmt_short_ast_long_comment(cmt: str, **extras) -> str:
    return "/*\n" + cmt + "*/\n"

def fmt_span_ast_long_comment(cmt: str, **extras) -> str:
    return (
            "/" + (extras["max_cols"] - 1)  * "*" + "\n" +
            cmt + "\n" +
            (extras["max_cols"] - 1) * "*" + "/" + "\n"
            )

def fmt_slash_slash_short_comment(cmt: str, **extras) -> str:
    return "// " + cmt + "\n"

def fmt_wrap_slash_slash_short_comment(cmt: str, **extras) -> str:
    return "// " + cmt + " //\n"

def fmt_wrap_long_short_comment(cmt: str, **extras) -> str:
    return "/* " + cmt + " */\n"

comment_wrappers["long"][LongCommentStyle.SPAN_AST] = (
        fmt_span_ast_long_comment
        )
comment_wrappers["long"][LongCommentStyle.SHORT_AST] = (
        fmt_short_ast_long_comment
        )
comment_wrappers["short"][ShortCommentStyle.SLASH_SLASH] = (
        fmt_slash_slash_short_comment
        )
comment_wrappers["short"][ShortCommentStyle.WRAP_SLASH_SLASH] = (
        fmt_wrap_slash_slash_short_comment
        )
comment_wrappers["short"][ShortCommentStyle.WRAP_LONG] = (
        fmt_wrap_long_short_comment
        )


class CFileWriter(fw.CodeWriter):

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

        self.long_comment_style = LongCommentStyle.SPAN_AST
        self.short_comment_style = ShortCommentStyle.SLASH_SLASH

        return

    def initialize_writer(self) -> None:
        self.long_comment_wrapper = comment_wrappers["long"][
                self.long_comment_style]
        self.short_comment_wrapper = comment_wrappers["short"][
                self.short_comment_style]

        self.header.wrap_fn = self.long_comment_wrapper
        self.footer.wrap_fn = self.short_comment_wrapper
        return


