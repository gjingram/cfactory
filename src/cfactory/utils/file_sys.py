import sys
import os
import traceback

class cd(object):

    def __init__(self, cd_to):
        self._cwd = os.getcwd()
        self._go_to = cd_to
        return

    def __enter__(self):
        os.chdir(self._go_to)
        return

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self._cwd)
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        return

def path_from_fs_root(path: str, start_from: str = os.getcwd()) -> str:
    return (
            path if path.startswith(os.sep) else
            os.path.normpath(
                os.path.join(
                    start_from,
                    path
                    )
                )
            )
