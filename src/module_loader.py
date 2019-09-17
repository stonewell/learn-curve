import importlib.util
import os
import sys

def load_module_from_file(module_file):
    module_name = os.path.basename(module_file)[:-3]
    try:
        return sys.modules[module_name]
    except KeyError:
        spec = importlib.util.spec_from_file_location(module_name, module_file)

        if spec is None:
            raise ValueError('unable load module from file:{}'.format(module_file))
        new_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(new_module)
        return new_module
