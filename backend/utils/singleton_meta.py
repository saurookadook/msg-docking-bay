"""A thread-safe metaclass for process-wide managers (PY-28)."""

import threading
from typing import Any, ClassVar, override


class SingletonMeta(type):
    """Make every call to a class return the same instance.

    The lock is checked twice so that the common case (the instance
    already exists) never waits on it, while two threads racing on
    the first call still build only one instance.
    """

    _instances: ClassVar[dict[SingletonMeta, object]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @override
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Return the only instance, building it on first use."""
        if cls not in SingletonMeta._instances:
            with SingletonMeta._lock:
                if cls not in SingletonMeta._instances:
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]
