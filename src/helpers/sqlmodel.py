import importlib
import inspect
import pkgutil

from sqlmodel import SQLModel


# This function dynamically imports all SQLModel table classes from the specified package.
# It ensures that every SQLModel with `table=True` in the package is registered in the global
# namespace.
def import_models_from_package(package):
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, SQLModel)
                and getattr(obj, "__table__", None) is not None
            ):
                globals()[name] = obj
