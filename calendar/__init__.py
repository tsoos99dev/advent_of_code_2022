import pkgutil

import solutions

for info in pkgutil.iter_modules(solutions.__path__):
    spec = info.module_finder.find_spec(info.name)
    spec.loader.load_module()

