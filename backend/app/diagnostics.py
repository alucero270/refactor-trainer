import json
import logging
import os
from collections import Counter
from threading import Lock
from typing import Any


logger = logging.getLogger("refactor_trainer.mvp")

DIAGNOSTICS_ENABLED_ENV = "REFACTOR_TRAINER_DIAGNOSTICS"

_SECRET_FIELD_MARKERS = ("api_key", "authorization", "secret", "token")
_ALLOWED_METRICS = {
    "attempt.evaluated",
    "attempt.failed",
    "candidates.listed",
    "exercise.failed",
    "exercise.generated",
    "github.connect.checked",
    "github.import.accepted",
    "github.import.rejected",
    "github.repos.listed",
    "github.tree.listed",
    "hints.failed",
    "hints.generated",
    "provider_config.updated",
    "submit_code.accepted",
    "submit_code.rejected",
}


def _diagnostics_enabled() -> bool:
    raw = os.environ.get(DIAGNOSTICS_ENABLED_ENV, "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


class BoundedMetrics:
    def __init__(self, allowed_names: set[str]) -> None:
        self._allowed_names = allowed_names
        self._counters: Counter[str] = Counter()
        self._lock = Lock()

    def increment(self, name: str) -> None:
        if name not in self._allowed_names:
            raise ValueError(f"Metric '{name}' is not registered.")
        if not _diagnostics_enabled():
            return
        with self._lock:
            self._counters[name] += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {name: self._counters.get(name, 0) for name in sorted(self._allowed_names)}

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()


metrics = BoundedMetrics(_ALLOWED_METRICS)


def log_event(event: str, **fields: Any) -> None:
    if not _diagnostics_enabled():
        return
    safe_fields = {key: _sanitize_field(key, value) for key, value in fields.items()}
    logger.info(json.dumps({"event": event, **safe_fields}, sort_keys=True))


def _sanitize_field(key: str, value: Any) -> Any:
    normalized_key = key.lower()
    if any(marker in normalized_key for marker in _SECRET_FIELD_MARKERS):
        return "[redacted]"
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_field(key, item) for item in value]
    if isinstance(value, dict):
        return {
            nested_key: _sanitize_field(str(nested_key), nested_value)
            for nested_key, nested_value in value.items()
        }
    return str(value)
