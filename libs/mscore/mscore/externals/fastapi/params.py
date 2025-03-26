from typing import Any, Callable, Optional, Sequence

from fastapi.params import Depends


class SecurityAcl(Depends):
    def __init__(
        self,
        dependency: Optional[Callable[..., Any]] = None,
        *,
        acl: Optional[Sequence[Any]] = None,
        use_cache: bool = True,
    ) -> None:
        super().__init__(dependency=dependency, use_cache=use_cache)
        self.acl = acl or []
