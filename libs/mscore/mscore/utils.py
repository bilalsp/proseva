#
# NOTE: type checking has been disable for this module in pyproject.toml
#
# import inspect
# from typing import Any
import json
import os
from functools import lru_cache

import requests
import toml


def get_project_version(file_path: str) -> str:
    """Extract project version from `pyproject.toml` file

    Args:
        file_path: path of `pyproject.toml` file.

    Returns:
        project version.
    """
    try:
        # Load the pyproject.toml file
        pyproject_data = toml.load(file_path)

        # Extract the version from the [tool.poetry] section
        version: str = pyproject_data["tool"]["poetry"]["version"]
        return version
    except (FileNotFoundError, KeyError) as ex:
        raise Exception(
            f"Error occurred while reading the project version from {file_path}: {ex}"
        ) from None


@lru_cache
def get_openapi_examples(examples_file: str, /) -> dict:
    """Get OpenAPI examples for the given examples-file.

    Args:
        examples_file: example file without `.json` extension.

    Returns:
        example dictionary.

    NOTE: It assumes that OpenAPI examples have been stored inside
        `examples` subdirectory at the project root.
    """
    examples_dir = "./openapi/examples"
    examples_file_path = os.path.join(examples_dir, f"{examples_file}.json")
    return json.load(open(examples_file_path, encoding="utf-8"))


@lru_cache
def get_openid_config(keycloak_server_url: str, realm_name: str) -> dict:
    url = f"{keycloak_server_url}/realms/{realm_name}/.well-known/openid-configuration"
    response = requests.get(url)  # TOOD: use httpx library
    response.raise_for_status()
    return response.json()


# #
# # TODO: deprecated metaclass...
# #
# class InstantiationMeta(type):
#     """This metaclass is responsible to instantiate class object with either given arguments or __init_from_settings__ class method."""

#     def __new__(cls, name, bases, attrs):
#         has_required_method = "__init_from_settings__" in attrs and isinstance(
#             attrs["__init_from_settings__"], staticmethod
#         )
#         if not has_required_method:
#             raise NotImplementedError(
#                 f"Class '{name}' must implement '__init_from_settings__' static method."
#             )
#         return super().__new__(cls, name, bases, attrs)

#     def __call__(cls, *args: Any, **kwargs: Any) -> Any:
#         new_args, new_kwargs = [], {}
#         ENV_VARS = cls.__init_from_settings__()
#         params = inspect.signature(cls.__init__).parameters.values()

#         for idx, param in enumerate(filter(lambda param: param.name != "self", params)):
#             match param.kind:
#                 case inspect.Parameter.POSITIONAL_ONLY:
#                     # Get from *args, ENV_VARS, or param.default
#                     if idx < len(args):
#                         new_args.append(args[idx])
#                     elif param.name in ENV_VARS:
#                         new_args.append(ENV_VARS[param.name])
#                     elif param.default != param.empty:
#                         new_args.append(param.default)
#                     else:
#                         # required POSITIONAL_ONLY argument is missing
#                         # error is raised by super().__call__
#                         break

#                 case inspect.Parameter.POSITIONAL_OR_KEYWORD:
#                     # Get from *args, kwargs, or ENV_VARS
#                     if idx < len(args):
#                         new_kwargs[param.name] = args[idx]
#                     elif param.name in kwargs:
#                         new_kwargs[param.name] = kwargs[param.name]
#                     elif param.name in ENV_VARS:
#                         new_kwargs[param.name] = ENV_VARS[param.name]

#                 case inspect.Parameter.KEYWORD_ONLY:
#                     # Get from kwargs, or ENV_VARS
#                     if param.name in kwargs:
#                         new_kwargs[param.name] = kwargs[param.name]
#                     elif param.name in ENV_VARS:
#                         new_args.append(ENV_VARS[param.name])

#                 case inspect.Parameter.VAR_POSITIONAL:
#                     raise NotImplementedError(
#                         "Class constructor with *args is not supported yet."
#                     )

#         # merge remaining keyword arguments into `new_kwargs`
#         new_kwargs |= dict(kwargs.items() - new_kwargs.items())

#         return super().__call__(*new_args, **new_kwargs)
