"""Command Line Interface for Assimilate Automation."""

import argparse
import json
import sys
from typing import List, Optional, Any

from src.core import (
    AssimilateCoreError,
    ValidationError,
    ProcessingError,
    ProcessingContext,
    process_batch,
)


def load_input_data(file_path: str) -> List[dict]:
    """Load JSON input data from a file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise argparse.ArgumentTypeError("Input JSON root must be a list of records.")
            return data
    except Exception as e:
        if isinstance(e, argparse.ArgumentTypeError):
            raise
        raise argparse.ArgumentTypeError(f"Failed to parse JSON file '{file_path}': {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Assimilate Automation CLI - Core Data Processing & Transformation Engine"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Process subcommand
    process_parser = subparsers.add_parser("process", help="Process and sanitize a batch of records")
    process_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to input JSON file containing records"
    )
    process_parser.add_argument(
        "-o", "--output",
        required=False,
        help="Path to output JSON file for processed results (default: stdout)"
    )
    process_parser.add_argument(
        "-r", "--required-keys",
        nargs="+",
        required=True,
        help="List of mandatory keys required for each record schema"
    )
    process_parser.add_argument(
        "--job-id",
        required=False,
        default="job_cli_default",
        help="Identifier for the processing job metadata"
    )
    process_parser.add_argument(
        "--source",
        required=False,
        default="cli_batch",
        help="Source identifier for the processing metadata"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = create_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.command == "process":
        try:
            records = load_input_data(args.input)
            context = ProcessingContext(job_id=args.job_id, source=args.source)
            processed_records = process_batch(records, args.required_keys, context=context)
            
            output_data = [pr.to_dict() for pr in processed_records]
            output_json = json.dumps(output_data, indent=2)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output_json)
            else:
                print(output_json)

            return 0
        except (ValidationError, ProcessingError, AssimilateCoreError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
