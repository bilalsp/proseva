from contextvars import ContextVar
from uuid import uuid4

# Context variable to store the request ID per async context (e.g., per request)
_request_id_context_var: ContextVar[str] = ContextVar(
    "request_id", default="default-request-id"
)


def get_request_id() -> str:
    """Retrieve the current request ID from the context variable.

    Returns:
        The current request ID. If none has been set in this context,
        returns the default value ('default-request-id').
    """
    return _request_id_context_var.get()


def new_request_id() -> str:
    """Generate a new unique request ID and set it in the context variable.

    This is typically called at the beginning of a request to initialize the
    request ID for the current async context.

    Returns:
        The newly generated request ID.
    """
    _request_id_context_var.set(str(uuid4()))
    return get_request_id()
