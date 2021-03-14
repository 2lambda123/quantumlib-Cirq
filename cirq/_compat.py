# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Workarounds for compatibility issues between versions and libraries."""
import functools
import importlib
import os
import re
import sys
import traceback
import warnings
from types import ModuleType
from typing import Any, Callable, Optional, Dict, Tuple, Type, Set

import numpy as np
import pandas as pd
import sympy


def proper_repr(value: Any) -> str:
    """Overrides sympy and numpy returning repr strings that don't parse."""

    if isinstance(value, sympy.Basic):
        result = sympy.srepr(value)

        # HACK: work around https://github.com/sympy/sympy/issues/16074
        # (only handles a few cases)
        fixed_tokens = ['Symbol', 'pi', 'Mul', 'Pow', 'Add', 'Mod', 'Integer', 'Float', 'Rational']
        for token in fixed_tokens:
            result = result.replace(token, 'sympy.' + token)

        return result

    if isinstance(value, np.ndarray):
        if np.issubdtype(value.dtype, np.datetime64):
            return f'np.array({value.tolist()!r}, dtype=np.{value.dtype!r})'
        return f'np.array({value.tolist()!r}, dtype=np.{value.dtype})'

    if isinstance(value, pd.MultiIndex):
        return f'pd.MultiIndex.from_tuples({repr(list(value))}, names={repr(list(value.names))})'

    if isinstance(value, pd.Index):
        return (
            f'pd.Index({repr(list(value))}, '
            f'name={repr(value.name)}, '
            f'dtype={repr(str(value.dtype))})'
        )

    if isinstance(value, pd.DataFrame):
        cols = [value[col].tolist() for col in value.columns]
        rows = list(zip(*cols))
        return (
            f'pd.DataFrame('
            f'\n    columns={proper_repr(value.columns)}, '
            f'\n    index={proper_repr(value.index)}, '
            f'\n    data={repr(rows)}'
            f'\n)'
        )

    return repr(value)


def proper_eq(a: Any, b: Any) -> bool:
    """Compares objects for equality, working around __eq__ not always working.

    For example, in numpy a == b broadcasts and returns an array instead of
    doing what np.array_equal(a, b) does. This method uses np.array_equal(a, b)
    when dealing with numpy arrays.
    """
    if type(a) == type(b):
        if isinstance(a, np.ndarray):
            return np.array_equal(a, b)
        if isinstance(a, (pd.DataFrame, pd.Index, pd.MultiIndex)):
            return a.equals(b)
        if isinstance(a, (tuple, list)):
            return len(a) == len(b) and all(proper_eq(x, y) for x, y in zip(a, b))
    return a == b


def _warn_or_error(msg, stacklevel=3):
    from cirq.testing.deprecation import ALLOW_DEPRECATION_IN_TEST

    called_from_test = 'PYTEST_CURRENT_TEST' in os.environ
    deprecation_allowed = ALLOW_DEPRECATION_IN_TEST in os.environ
    if called_from_test and not deprecation_allowed:
        raise ValueError(f"Cirq should not use deprecated functionality: {msg}")

    warnings.warn(
        msg,
        DeprecationWarning,
        stacklevel=stacklevel,
    )


def _validate_deadline(deadline: str):
    DEADLINE_REGEX = r"^v(\d)+\.(\d)+$"
    assert re.match(DEADLINE_REGEX, deadline), "deadline should match vX.Y"


def deprecated(
    *, deadline: str, fix: str, name: Optional[str] = None
) -> Callable[[Callable], Callable]:
    """Marks a function as deprecated.

    Args:
        deadline: The version where the function will be deleted. It should be a minor version
            (e.g. "v0.7").
        fix: A complete sentence describing what the user should be using
            instead of this particular function (e.g. "Use cos instead.")
        name: How to refer to the function.
            Defaults to `func.__qualname__`.

    Returns:
        A decorator that decorates functions with a deprecation warning.
    """
    _validate_deadline(deadline)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def decorated_func(*args, **kwargs) -> Any:
            qualname = func.__qualname__ if name is None else name
            _warn_or_error(
                f'{qualname} was used but is deprecated.\n'
                f'It will be removed in cirq {deadline}.\n'
                f'{fix}\n'
            )

            return func(*args, **kwargs)

        decorated_func.__doc__ = (
            f'THIS FUNCTION IS DEPRECATED.\n\n'
            f'IT WILL BE REMOVED IN `cirq {deadline}`.\n\n'
            f'{fix}\n\n'
            f'{decorated_func.__doc__ or ""}'
        )

        return decorated_func

    return decorator


def deprecated_class(
    *, deadline: str, fix: str, name: Optional[str] = None
) -> Callable[[Type], Type]:
    """Marks a class as deprecated.

    Args:
        deadline: The version where the function will be deleted. It should be a minor version
            (e.g. "v0.7").
        fix: A complete sentence describing what the user should be using
            instead of this particular function (e.g. "Use cos instead.")
        name: How to refer to the class.
            Defaults to `class.__qualname__`.

    Returns:
        A decorator that decorates classes with a deprecation warning.
    """

    _validate_deadline(deadline)

    def decorator(clazz: Type) -> Type:
        clazz_new = clazz.__new__

        def patched_new(cls, *args, **kwargs):
            qualname = clazz.__qualname__ if name is None else name
            _warn_or_error(
                f'{qualname} was used but is deprecated.\n'
                f'It will be removed in cirq {deadline}.\n'
                f'{fix}\n'
            )

            return clazz_new(cls)

        setattr(clazz, '__new__', patched_new)
        clazz.__doc__ = (
            f'THIS CLASS IS DEPRECATED.\n\n'
            f'IT WILL BE REMOVED IN `cirq {deadline}`.\n\n'
            f'{fix}\n\n'
            f'{clazz.__doc__ or ""}'
        )

        return clazz

    return decorator


def deprecated_parameter(
    *,
    deadline: str,
    fix: str,
    func_name: Optional[str] = None,
    parameter_desc: str,
    match: Callable[[Tuple[Any, ...], Dict[str, Any]], bool],
    rewrite: Optional[
        Callable[[Tuple[Any, ...], Dict[str, Any]], Tuple[Tuple[Any, ...], Dict[str, Any]]]
    ] = None,
) -> Callable[[Callable], Callable]:
    """Marks a function parameter as deprecated.

    Also handles rewriting the deprecated parameter into the new signature.

    Args:
        deadline: The version where the function will be deleted. It should be a minor version
            (e.g. "v0.7").
        fix: A complete sentence describing what the user should be using
            instead of this particular function (e.g. "Use cos instead.")
        func_name: How to refer to the function.
            Defaults to `func.__qualname__`.
        parameter_desc: The name and type of the parameter being deprecated,
            e.g. "janky_count" or "janky_count keyword" or
            "positional janky_count".
        match: A lambda that takes args, kwargs and determines if the
            deprecated parameter is present or not. This determines whether or
            not the deprecation warning is debuged, and also whether or not
            rewrite is called.
        rewrite: Returns new args/kwargs that don't use the deprecated
            parameter. Defaults to making no changes.

    Returns:
        A decorator that decorates functions with a parameter deprecation
            warning.
    """
    _validate_deadline(deadline)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def decorated_func(*args, **kwargs) -> Any:
            if match(args, kwargs):
                if rewrite is not None:
                    args, kwargs = rewrite(args, kwargs)

                qualname = func.__qualname__ if func_name is None else func_name
                _warn_or_error(
                    f'The {parameter_desc} parameter of {qualname} was '
                    f'used but is deprecated.\n'
                    f'It will be removed in cirq {deadline}.\n'
                    f'{fix}\n',
                )

            return func(*args, **kwargs)

        return decorated_func

    return decorator


def deprecate_attributes(module: ModuleType, deprecated_attributes: Dict[str, Tuple[str, str]]):
    """Wrap a module with deprecated attributes that give warnings.

    Args:
        module: The module to wrap.
        deprecated_attributes: A dictionary from attribute name to a tuple of
            strings, where the first string gives the version that the attribute
            will be removed in, and the second string describes what the user
            should do instead of accessing this deprecated attribute.

    Returns:
        Wrapped module with deprecated attributes. Use of these attributes
        will cause a warning for these deprecated attributes.
    """

    for (deadline, _) in deprecated_attributes.values():
        _validate_deadline(deadline)

    class Wrapped(ModuleType):

        __dict__ = module.__dict__

        def __getattr__(self, name):
            if name in deprecated_attributes:
                deadline, fix = deprecated_attributes[name]
                _warn_or_error(
                    f'{name} was used but is deprecated.\n'
                    f'It will be removed in cirq {deadline}.\n'
                    f'{fix}\n'
                )
            return getattr(module, name)

    return Wrapped(module.__name__, module.__doc__)


class AliasingLoader(importlib.abc.Loader):
    """A module loader used to hook the python import statement."""

    def __init__(self, loader: Any, old_prefix: str, new_prefix: str):
        """A module loader that uses an existing module loader and intercepts
        the execution of a module.
        """

        def wrap_exec_module(method: Any) -> Any:
            def exec_module(module: ModuleType) -> None:
                if not module.__name__.startswith(
                    self.old_prefix
                ) and not module.__name__.startswith(self.new_prefix):
                    return method(module)

                old_module_is_not_cached_yet = module.__name__.startswith(self.old_prefix)
                if old_module_is_not_cached_yet:
                    new_module_name = module.__name__.replace(self.old_prefix, self.new_prefix)
                    old_module_name = module.__name__
                    # check for new_module whether it was loaded
                    if new_module_name in sys.modules:
                        # found it - no need to load the module again
                        sys.modules[old_module_name] = sys.modules[new_module_name]
                        return
                else:
                    # new module is not cached yet
                    new_module_name = module.__name__
                    old_module_name = module.__name__.replace(self.new_prefix, self.old_prefix)
                    # check for old_module whether it was loaded first
                    if old_module_name in sys.modules:
                        # found it - no need to load the module again
                        sys.modules[new_module_name] = sys.modules[old_module_name]
                        return

                # now we know we have to initialize the module
                sys.modules[old_module_name] = module
                sys.modules[new_module_name] = module

                try:
                    _debug(f"exec module: {module}. Now {new_module_name} is cached.")
                    res = method(module)
                    _debug(f"res: {res}")
                    return res
                except Exception as ex:
                    # if there's an error, we atomically remove both
                    del sys.modules[new_module_name]
                    del sys.modules[old_module_name]
                    raise ex

            return exec_module

        def wrap_load_module(method: Any) -> Any:
            _debug(f"has a loadmodule! wrapping...")

            def load_module(fullname: str) -> ModuleType:
                _debug(f"load_module: {fullname}.")
                if fullname == self.old_prefix:
                    mod = method(self.new_prefix)
                    return mod
                return method(fullname)

            return load_module

        _debug(f"wrapping: {old_prefix} --> {new_prefix}")
        self.loader = loader
        if hasattr(loader, 'exec_module'):
            self.exec_module = wrap_exec_module(loader.exec_module)
        if hasattr(loader, 'load_module'):
            self.load_module = wrap_load_module(loader.load_module)
        self.old_prefix = old_prefix
        self.new_prefix = new_prefix

    def create_module(self, spec: ModuleType) -> ModuleType:
        _debug(f"create_mod: {spec}")
        return self.loader.create_module(spec)

    def module_repr(self, module: ModuleType) -> str:
        _debug(f"module_repr: {module.__name__}")
        return self.loader.module_repr(module)

    def __repr__(self):
        return f"AliasingLoader: {self.old_prefix} -> {self.new_prefix} wrapping {self.loader}"


def _debug(*args):
    pass
    # print(*args)


class DeprecatedModuleFinder(importlib.abc.MetaPathFinder):
    """A module finder used to hook the python import statement."""

    _warned: Set[str] = set()

    def __init__(
        self,
        finder: Any,
        new_module_name: str,
        new_module_spec: importlib._bootstrap.ModuleSpec,
        old_module_name: str,
        deadline: str,
    ):
        """An aliasing module finder that uses an existing module finder to find a python
        module spec and intercept the execution of matching modules.
        """
        self.finder = finder
        self.new_module_name = new_module_name
        self.old_module_name = old_module_name
        self.new_module_spec = new_module_spec
        self.deadline = deadline
        # to cater for metadata path finders
        # https://docs.python.org/3/library/importlib.metadata.html#extending-the-search-algorithm
        if hasattr(finder, "find_distributions"):
            self.find_distributions = getattr(finder, "find_distributions")

    def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> Any:
        if not fullname.startswith(self.old_module_name) and not fullname.startswith(
            self.new_module_name
        ):
            return self.finder.find_spec(fullname, path, target)

        self.handle_deprecation_warning(fullname)

        new_fullname = fullname.replace(self.old_module_name, self.new_module_name)
        if fullname == self.old_module_name:
            spec = self.new_module_spec
        else:
            # we are finding a submodule of the deprecated module
            spec = self.finder.find_spec(
                new_fullname,
                path=self.new_module_spec.submodule_search_locations + path,
                target=target,
            )
        if spec is not None and fullname.startswith(self.old_module_name):
            if spec.loader.name == new_fullname:
                spec.loader.name = fullname
            spec.loader = AliasingLoader(spec.loader, fullname, new_fullname)
            spec.name = fullname

        _debug(f"find_spec result: {fullname} - {spec}")
        return spec

    def handle_deprecation_warning(self, fullname):
        if (
            fullname.startswith(self.old_module_name)
            and self.old_module_name not in DeprecatedModuleFinder._warned
        ):
            DeprecatedModuleFinder._warned.add(self.old_module_name)

            # find the first frame that is not this file or importlib land
            file, deprecation_level = next(
                filter(
                    lambda indexed_frame_file: (
                        "importlib" not in indexed_frame_file[0]
                        and "cirq/_compat.py" not in indexed_frame_file[0]
                    ),
                    [(frame[0], i) for i, frame in enumerate(reversed(traceback.extract_stack()))],
                )
            )

            _warn_or_error(
                f"{file, deprecation_level}! import {self.old_module_name} is deprecated, "
                f"it will be removed in version {self.deadline}, "
                f"use {self.new_module_name} instead.",
                stacklevel=deprecation_level,
            )


sys.deprecating = []


def deprecated_submodule(*, new_module_name: str, old_parent: str, old_child: str, deadline: str):
    """Creates a deprecated module reference recursively for a module.

    For `new_module_name` (e.g. cirq_google) creates an alias (e.g cirq.google) in Python's module
    cache. It also recursively checks for the already imported submodules (e.g. cirq_google.api) and
    creates the alias for them too (e.g. cirq.google.api). With this method it is possible to create
    an alias that really looks like a module, e.g you can do things like
    `from cirq.google import api` - which would be otherwise impossible.

    Note that this method will execute `new_module_name` in order to ensure that it is in the module
    cache.

    While it is not recommended, one could even use this to make this work:

    >>> import numpy as np
    >>> import cirq._import
    >>> cirq._import.deprecated_submodule('numpy', 'np')
    >>> from np import linalg # which would otherwise fail!

    Args:
        new_module_name: absolute module name for the new module
        old_parent: the current module that had the original submodule
        old_child: the submodule that is being relocated
    Returns:
        None
    Raises:
          AssertionError - when the
    """

    old_module_name = f"{old_parent}.{old_child}"

    _debug(f"deprecating {old_module_name} -> {new_module_name}")

    new_module_spec = importlib.util.find_spec(new_module_name)

    def wrap(finder: Any) -> Any:
        if not hasattr(finder, 'find_spec'):
            return finder
        return DeprecatedModuleFinder(
            finder, new_module_name, new_module_spec, old_module_name, deadline
        )

    sys.meta_path = [wrap(finder) for finder in sys.meta_path]

    _debug(f"DONE depr {old_module_name} -> {new_module_name}")
