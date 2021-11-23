
def strip_final_comma(text: str) -> str:
    return text.rstrip(',')

def strip_initial_comma(text: str) -> str:
    return text.lstrip(',')

def replace_semi_colons(text: str) -> str:
    return text.replace(';', '\n')

