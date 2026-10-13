"""Regression tests for input parsing, integrity checks and API errors."""
import json
import math

import pytest
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from csv_utils import parse_bool
from immunotherapy_response_agent.agents import IOOrchestrator
from immunotherapy_response_agent.models import ClinicalCasePayload


@pytest.mark.parametrize("raw,expected", [
    (True, True), (False, False), ("True", True), ("False", False),
    ("1", True), ("0", False), ("YES", True), ("off", False), ("", False),
])
def test_csv_boolean_values(raw, expected):
    assert parse_bool(raw) is expected


def test_csv_boolean_unknown_rejected():
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_audit_signature_and_chain_tampering():
    trail = AuditTrail(secret_key="test-key")
    trail.log("actor", "tier", "event", {"value": 1})
    trail.log("actor", "tier", "event", {"value": 2})
    assert trail.verify_integrity()
    exposed = trail.get_trail()
    exposed[0]["event_type"] = "modified"
    assert trail.verify_integrity()  # public snapshot cannot mutate internal records
    trail.logs[0]["event_type"] = "modified"
    assert not trail.verify_integrity()  # HMAC verification catches original-block tampering


def test_audit_signature_tampering_last_block():
    trail = AuditTrail(secret_key="test-key")
    trail.log("actor", "tier", "event", {"value": 1})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_metrics_rejected(invalid):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T1", target_identifier="S1", primary_metric=invalid)


def test_attributes_are_checked_for_identifier_patterns():
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="S1", primary_metric=1,
        attributes={"contact": "john.doe@hospital.org"}
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


def test_secondary_clinical_package_executes():
    dossier = IOOrchestrator().process_case(ClinicalCasePayload(
        case_id="TEST-001", patient_synthetic_id="S1",
        primary_metric=1.0, secondary_metric=1.0, status_flag="NORMAL"
    ))
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"


def test_api_rejects_identifier_with_client_error():
    from fastapi.testclient import TestClient
    from agents.api import app
    with TestClient(app) as client:
        result = client.post("/api/audit", json={
            "task_id": "T1", "target_identifier": "S1", "primary_metric": 1,
            "attributes": {"email": "john.doe@hospital.org"}
        })
    assert result.status_code == 422
    assert "john.doe@hospital.org" not in result.text


def test_batch_csv_false_and_true_are_distinct(tmp_path):
    import csv
    from cli import main
    source = tmp_path / "cases.csv"
    destination = tmp_path / "results.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\\n"
        "C1,SYNTH-01,10,3,False,NOMINAL\\n"
        "C2,SYNTH-02,10,3,True,NOMINAL\\n",
        encoding="utf-8"
    )
    assert main(["batch", "--input", str(source), "--output", str(destination)]) == 0
    with destination.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ROUTINE"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"


def test_clinical_prototype_api_rejects_nonfinite_values():
    from fastapi.testclient import TestClient
    from immunotherapy_response_agent.server import create_app
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/api/audit", json={"primary_metric": "inf"})
    assert response.status_code == 422
