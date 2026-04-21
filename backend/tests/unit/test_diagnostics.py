import json
import logging

import pytest

from app.diagnostics import log_event, metrics


def test_metrics_are_bounded_to_registered_names():
    metrics.increment("submit_code.accepted")

    snapshot = metrics.snapshot()

    assert snapshot["submit_code.accepted"] == 1
    assert snapshot["attempt.evaluated"] == 0
    with pytest.raises(ValueError, match="not registered"):
        metrics.increment("unbounded.metric")


def test_structured_logs_redact_secret_fields(caplog):
    caplog.set_level(logging.INFO, logger="refactor_trainer.mvp")

    log_event(
        "provider_config.updated",
        default_provider="openai",
        api_key="secret-value",
        nested={"token": "ghp-secret"},
    )

    payload = json.loads(caplog.records[0].message)
    assert payload == {
        "event": "provider_config.updated",
        "default_provider": "openai",
        "api_key": "[redacted]",
        "nested": {"token": "[redacted]"},
    }
