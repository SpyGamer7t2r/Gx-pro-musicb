import os
from os.path import dirname, isfile, join

def __list_all_modules():
    plugin_dir = dirname(__file__)
    all_files = os.listdir(plugin_dir)
    all_modules = []

    for file in all_files:
        full_path = join(plugin_dir, file)
        if isfile(full_path) and file.endswith(".py") and file != "__init__.py":
            all_modules.append(file[:-3])  # remove .py

    return all_modules

ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]