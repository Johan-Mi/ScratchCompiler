"""This module contains the ScratchIndenter class, which handles indentation for the parser."""
from lark.indenter import Indenter


class ScratchIndenter(Indenter):
    """The indenter used for the scratch parser."""
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4
