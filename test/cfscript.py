import cfactory.factory as factory
import os


factory.project_name = "cfactory_test"
factory.cache_dir = "cfactory_test_cache"
factory.ccm_state_dir = os.path.join(factory.cache_dir, "ccm_test")


