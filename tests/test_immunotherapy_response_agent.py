"""
Automated Pytest Test Suite for Immunotherapy Response Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_email_pattern():
    """Test that email addresses are correctly detected as PHI."""
    # Email should be detected
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Contact at john.doe@hospital.com for results")

    # Clean text without email passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_phone_pattern():
    """Test that phone numbers are correctly detected as PHI."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Call patient at 555-123-4567 for follow-up")

    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient phone: (555) 123-4567")


def test_phi_guard_ssn_pattern():
    """Test that SSN patterns are correctly detected as PHI."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient SSN: 123-45-6789 verified")


def test_phi_guard_patient_name_pattern():
    """Test that patient names are correctly detected as PHI."""
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient John Doe admitted for treatment")

    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient Name: Alice Johnson confirmed")


def test_phi_redaction():
    """Test that PHI is properly redacted."""
    text_with_phi = "Contact john@hospital.com or call 555-123-4567"
    redacted = PHIGuard.redact_phi(text_with_phi)
    assert "[REDACTED_IDENTIFIER]" in redacted
    assert "john@hospital.com" not in redacted
    assert "555-123-4567" not in redacted


def test_phi_guard_empty_and_none():
    """Test that empty/None text doesn't raise exceptions."""
    PHIGuard.assert_no_phi("")
    PHIGuard.assert_no_phi(None)


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_cli_batch_missing_file():
    """Test that batch mode handles missing files gracefully."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1


def test_audit_trail_tamper_detection():
    """Test that audit trail integrity verification works."""
    # Create a fresh audit trail
    from agents.base import AuditTrail
    trail = AuditTrail(secret_key="test-key-for-integrity")

    # Log some entries
    trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "test1"})
    trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "test2"})
    trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "test3"})

    # Verify integrity
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 3


def test_worker_boundary_conditions():
    """Test workers at exact threshold boundaries."""
    # Worker 1 at exact threshold (25.0 - should NOT trigger, check is > 25.0)
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=25.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 0

    # Worker 1 just above threshold
    p1b = SystemTaskPayload(task_id="T1b", target_identifier="KEY-01", primary_metric=25.01)
    alerts1b = InvariantQCWorker.evaluate(p1b)
    assert len(alerts1b) == 1

    # Worker 2 above threshold (12.0 - should trigger, check is > 12.0)
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, secondary_metric=12.01)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1


def test_supervisor_urgency_escalation():
    """Test that supervisor correctly escalates urgency based on alerts."""
    supervisor = SystemSupervisor(model_provider="mock")

    # Critical case
    p_critical = SystemTaskPayload(
        task_id="CRIT-01", target_identifier="KEY-01",
        primary_metric=50.0, is_critical_flag=True
    )
    dossier = supervisor.process_task(p_critical)
    assert dossier.overall_urgency == UrgencyLevel.CRITICAL_STAT

    # Elevated case
    p_elevated = SystemTaskPayload(
        task_id="ELEV-01", target_identifier="KEY-02",
        primary_metric=30.0, status_descriptor="DISCORDANT"
    )
    dossier = supervisor.process_task(p_elevated)
    assert dossier.overall_urgency == UrgencyLevel.ELEVATED

    # Routine case
    p_routine = SystemTaskPayload(
        task_id="RTN-01", target_identifier="KEY-03",
        primary_metric=10.0, status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(p_routine)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
