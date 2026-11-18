"""Core data processing utilities and robust exception handling.

Provides typed dataclasses, robust validation utilities, and custom exceptions
for enterprise data pipelines.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class AssimilateCoreError(Exception):
    """Base exception class for all core module errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AssimilateCoreError):
    """Raised when data validation fails against expected schemas or dataclasses."""
    pass


class ProcessingError(AssimilateCoreError):
    """Raised when data transformation or processing encounters an unrecoverable error."""
    pass


@dataclass
class ProcessingContext:
    """Execution context carrying metadata and audit trail for data processing."""
    job_id: str
    source: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ProcessedRecord:
    """Represents a successfully processed data record."""
    record_id: str
    raw_data: Dict[str, Any]
    transformed_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "SUCCESS"


def validate_record_schema(record: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validates that a record dictionary contains all required keys.

    Args:
        record: Dictionary representing a data record.
        required_keys: List of mandatory keys that must be present.

    Returns:
        True if all required keys are present and non-null.

    Raises:
        ValidationError: If any required key is missing or None.
    """
    if not isinstance(record, dict):
        raise ValidationError(f"Record must be a dictionary, got {type(record).__name__}")

    missing = [key for key in required_keys if key not in record or record[key] is None]
    if missing:
        raise ValidationError(
            f"Validation failed. Missing or null required keys: {missing}",
            details={"missing_keys": missing, "record_keys": list(record.keys())}
        )
    return True


def sanitize_string_fields(record: Dict[str, Any], fields_to_sanitize: List[str]) -> Dict[str, Any]:
    """Strips leading/trailing whitespace from specified string fields in a record.

    Args:
        record: Input record dictionary.
        fields_to_sanitize: List of keys whose string values should be cleaned.

    Returns:
        A new dictionary with sanitized string fields.
    """
    sanitized = record.copy()
    for field_name in fields_to_sanitize:
        if field_name in sanitized and isinstance(sanitized[field_name], str):
            sanitized[field_name] = sanitized[field_name].strip()
    return sanitized


def process_batch(
    records: List[Dict[str, Any]],
    required_keys: List[str],
    context: Optional[ProcessingContext] = None
) -> List[ProcessedRecord]:
    """Processes a batch of records with schema validation and sanitization.

    Args:
        records: List of raw data record dictionaries.
        required_keys: Mandatory keys required in each record.
        context: Optional processing context for audit logging.

    Returns:
        List of ProcessedRecord instances.

    Raises:
        ValidationError: If any record fails schema validation.
    """
    logger.info("Starting batch processing of %d records", len(records))
    processed_results: List[ProcessedRecord] = []

    for index, raw_record in enumerate(records):
        try:
            validate_record_schema(raw_record, required_keys)
            
            # Determine record identifier
            record_id = str(raw_record.get("id", raw_record.get("record_id", f"rec_{index}")))
            
            # Perform sanitization on common string fields if present
            sanitized = sanitize_string_fields(raw_record, ["name", "title", "description", "category"])
            
            processed_record = ProcessedRecord(
                record_id=record_id,
                raw_data=raw_record,
                transformed_data=sanitized,
                metadata={
                    "batch_index": index,
                    "job_id": context.job_id if context else "adhoc",
                    "source": context.source if context else "unknown"
                }
            )
            processed_results.append(processed_record)
        except ValidationError as ve:
            logger.error("Validation error at record index %d: %s", index, ve)
            raise
        except Exception as e:
            logger.error("Unexpected error processing record index %d: %s", index, e)
            raise ProcessingError(
                f"Failed to process record at index {index}: {str(e)}",
                details={"index": index, "raw_record": raw_record}
            ) from e

    logger.info("Successfully processed batch of %d records", len(processed_results))
    return processed_results
