from typing import Any, Callable, Optional, Sequence

from . import params


def SecurityAcl(
    dependency: Optional[Callable[..., Any]] = None,
    *,
    acl: Optional[Sequence[Any]] = None,
    use_cache: bool = True,
) -> params.SecurityAcl:
    return params.SecurityAcl(dependency=dependency, acl=acl, use_cache=use_cache)
