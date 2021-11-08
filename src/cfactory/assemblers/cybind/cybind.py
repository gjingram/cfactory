import sys
import cfactory.__config__.cfactory_config as cfg
import cfactory.factory as factory

cybind_project_root = ""
module_registry = {}
header_map = {}

def register_module(cybind_module: "CybindModule") -> bool:
    if cybind_module in module_registry.values():
        cfg.cfactory_logger.bind(color="red").opt(colors=True).error(
                f"Cybind module \"{cybind_module.module_name}\"" +
                "already_registered"
                )
        sys.exit(-1)
    module_registry[cybind_module.module_name] = cybind_module
    map_headers(cybind_module)
    return

def map_headers(cybind_module: "CybindModule") -> None:
    header_map[cybind_module.header] = cybind_module.module_name
    return
