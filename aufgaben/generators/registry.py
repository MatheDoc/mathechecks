import inspect
import pkgutil
from importlib import import_module

from aufgaben.generators import __path__ as GENERATOR_PACKAGE_PATH
from aufgaben.generators.base import TaskGenerator


def _import_generator_modules() -> None:
    prefix = "aufgaben.generators."
    for module_info in pkgutil.walk_packages(GENERATOR_PACKAGE_PATH, prefix=prefix):
        module_name = module_info.name
        module_leaf = module_name.rsplit(".", 1)[-1]
        if module_leaf in {"base", "registry"}:
            continue
        import_module(module_name)


def _iter_concrete_generators() -> list[type[TaskGenerator]]:
    discovered: list[type[TaskGenerator]] = []
    stack = list(TaskGenerator.__subclasses__())
    seen: set[type[TaskGenerator]] = set()

    while stack:
        candidate = stack.pop()
        if candidate in seen:
            continue
        seen.add(candidate)
        stack.extend(candidate.__subclasses__())

        if inspect.isabstract(candidate):
            continue
        discovered.append(candidate)

    return discovered


def _build_registry() -> dict[str, type[TaskGenerator]]:
    _import_generator_modules()

    registry: dict[str, type[TaskGenerator]] = {}
    for generator_class in _iter_concrete_generators():
        key = generator_class.generator_key
        if not key:
            raise ValueError(
                f"Generator-Klasse {generator_class.__name__} definiert keinen generator_key."
            )
        if key in registry:
            raise ValueError(f"Doppelter generator_key registriert: {key}")
        registry[key] = generator_class

    return registry


REGISTRY: dict[str, type[TaskGenerator]] = _build_registry()


def build_generator(generator_key: str) -> TaskGenerator:
    try:
        generator_class = REGISTRY[generator_key]
    except KeyError as exc:
        raise ValueError(f"Unbekannter Generator: {generator_key}") from exc
    return generator_class()
