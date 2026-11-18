"""Tests for the Assimilate Automation core module."""

import pytest
from src.core import (
    AssimilateCoreError,
    ValidationError,
    ProcessingError,
    ProcessingContext,
    ProcessedRecord,
    validate_record_schema,
    sanitize_string_fields,
    process_batch,
)


def test_validate_record_schema_success():
    record = {"id": "123", "name": "  Test Item  ", "value": 42}
    assert validate_record_schema(record, ["id", "name"]) is True


def test_validate_record_schema_missing_key():
    record = {"id": "123"}
    with pytest.raises(ValidationError) as exc_info:
        validate_record_schema(record, ["id", "name"])
    assert "missing_keys" in exc_info.value.details
    assert "name" in exc_info.value.details["missing_keys"]


def test_validate_record_schema_none_value():
    record = {"id": "123", "name": None}
    with pytest.raises(ValidationError):
        validate_record_schema(record, ["id", "name"])


def test_validate_record_schema_not_dict():
    with pytest.raises(ValidationError):
        validate_record_schema(["not", "a", "dict"], ["id"])  # type: ignore


def test_sanitize_string_fields():
    record = {"name": "  Enterprise Core  ", "title": "\tEngine\n", "value": 100}
    sanitized = sanitize_string_fields(record, ["name", "title"])
    assert sanitized["name"] == "Enterprise Core"
    assert sanitized["title"] == "Engine"
    assert sanitized["value"] == 100


def test_process_batch_success():
    context = ProcessingContext(job_id="job_001", source="unit_test")
    records = [
        {"id": "r1", "name": " Alpha "},
        {"id": "r2", "name": "Beta"},
    ]
    results = process_batch(records, ["id", "name"], context=context)
    
    assert len(results) == 2
    assert isinstance(results[0], ProcessedRecord)
    assert results[0].record_id == "r1"
    assert results[0].transformed_data["name"] == "Alpha"
    assert results[0].metadata["job_id"] == "job_001"
    assert results[0].metadata["source"] == "unit_test"


def test_process_batch_validation_failure():
    records = [
        {"id": "r1", "name": "Alpha"},
        {"id": "r2"},  # Missing 'name'
    ]
    with pytest.raises(ValidationError):
        process_batch(records, ["id", "name"])
