import cfactory.factory as factory
from cfactory.assemblers.cybind.assembler import CybindAssembler
import os

factory.project_name = "cfactory_test"
factory.cache_dir = "cfactory_test_cache"
factory.ccm_state_dir = os.path.join(factory.cache_dir, "ccm_test")

cybind = CybindAssembler("test")
cybind.add_files("test_hh/*.hh")
