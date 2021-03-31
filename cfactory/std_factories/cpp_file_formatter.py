import illuminate.std_factories.file_formatter as ffmat
import illuminate.__config__.illuminate_config as il_cfg


cpp_scope = [
        '::'
        ]
cpp_postfix = [
        '++',
        '--',
        '.'
        ]
cpp_ptr_access = [
        '->'
        ]
cpp_left_brackets = [
        '<',
        '[',
        '('
        ]
cpp_right_brackets = [
        '>',
        ']',
        ')'
        ]
cpp_prefix = [
        '++',
        '--',
        '~',
        '!',
        '+',
        '-',
        '*',
        '&'
        ]
cpp_prefix_kwords = [
        'new',
        'delete',
        'sizeof'
        ]
cpp_ptr_to_member = [
        '.*',
        '->*'
        ]
cpp_arithmetic = [
        '*',
        '/',
        '%',
        '+',
        '-'
        ]
cpp_bitwise = [
        '<<',
        '>>',
        '&',
        '^',
        '|'
        ]
cpp_relational = [
        '==',
        '!=',
        '>=',
        '<=',
        '<',
        '>'
        ]
cpp_logical = [
        '&&',
        '||'
        ]
cpp_assignment = [
    '>>=',
    '<<=',
    '*=',
    '*=',
    '/=',
    '%=',
    '+=',
    '-=',
    '&=',
    '^=',
    '|=',
    '='
    ]
cpp_conditional = [
    '?'
    ]
cpp_access_kwords = [
    'public:',
    'protected:',
    'private:'
    ]
cpp_sequencing = [
    ','
    ]
cpp_expr_term = [
    ';'
    ]


class CppFileFormatter(ffmat.FileFormatter):

    def __init__(self):
        ffmat.FileFormatter.__init__(self)
        self.indent_char = il_cfg.cpp_indent_char
        self.indent_size = il_cfg.cpp_indent_size
        self.max_line_len = il_cfg.cpp_max_line_len
        self.src_ext = il_cfg.cpp_src_ext
        self.header_ext = il_cfg.cpp_header_ext
        self.template_ext = il_cfg.cpp_template_ext

        self.language = ['c++', 'cpp', 'cc']
        self.split_tokens.extend(cpp_scope)
        self.split_tokens.extend(cpp_postfix)
        self.split_tokens.extend(cpp_ptr_access)
        self.split_tokens.extend(cpp_left_brackets)
        self.split_tokens.extend(cpp_ptr_to_member)
        self.split_tokens.extend(cpp_bitwise)
        self.split_tokens.extend(cpp_relational)
        self.split_tokens.extend(cpp_logical)
        self.split_tokens.extend(cpp_assignment)
        self.split_tokens.extend(cpp_conditional)
        self.split_tokens.extend(cpp_access_kwords)
        self.split_tokens.extend(cpp_sequencing)
        self.split_tokens.extend(cpp_expr_term)
        self.split_tokens.append(':')

        self.split_tokens_nl.append('.')
        self.split_tokens_nl.append('.*')
        self.split_tokens_nl.append('->')
        self.split_tokens_nl.append('->*')
        self.split_tokens_nl.append('&')

        self.ext_matches = ['.cc', '.cpp', '.h', '.hh', '.hpp', '.tpp']

        return
