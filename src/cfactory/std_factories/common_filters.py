import pathlib

def filename(path: str) -> str:
    return pathlib.Path(path).stem

def local_module_name(from_root: str) -> str:
    return from_root.split('.')[-1]

def param_list(params: typing.List[str]) -> str:
    return "".join(params, ", ")
