import importlib
import logging


def import_modules(file_name, module_list):
    """Importeer modules vanuit een lijst met strings."""
    imported, error = {}, False

    for name in module_list:
        try:
            module = importlib.import_module(name)
            imported[name] = module
            logging.info(f"Succesvol geïmporteerd: {name} in file: {file_name}")
        except ImportError as e:
            logging.error(f"Kon {name} niet importeren: {e} in file: {file_name}")
            error = True 
    return imported, error

