import importlib
import os

def load_components(path="components"):

    components = {}
    for filename in os.listdir(path):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]

            try:

                module = importlib.import_module(f"{path}.{module_name}")

                if hasattr(module, module_name):
                    components[module_name.capitalize()] = getattr(module, module_name)
            except(ImportError, AttributeError) as e:
                print(f"Erro ao carregar `{filename}")
    return components
