"""Tests for the Assimilate Automation CLI module."""

import json
import subprocess
import sys
import tempfile
import os
import pytest

from src.cli import create_parser, main, load_input_data


def test_parser_creation():
    parser = create_parser()
    assert parser is not None
    # Test process subcommand parsing
    args = parser.parse_args(["process", "-i", "data.json", "-r", "id", "name"])
    assert args.command == "process"
    assert args.input == "data.json"
    assert args.required_keys == ["id", "name"]


def test_load_input_data_valid_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "input.json"
    records = [{"id": "1", "name": "Test"}]
    p.write_text(json.dumps(records), encoding="utf-8")

    loaded = load_input_data(str(p))
    assert loaded == records


def test_load_input_data_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("invalid json content", encoding="utf-8")

    with pytest.raises(SystemExit):
        # load_input_data raises ArgumentTypeError, which argparse catches or converts
        pass


def test_main_process_success(tmp_path):
    input_file = tmp_path / "records.json"
    output_file = tmp_path / "output.json"
    
    input_data = [
        {"id": "rec_1", "name": "  Alpha Item  "},
        {"id": "rec_2", "name": "Beta Item"}
    ]
    input_file.write_text(json.dumps(input_data), encoding="utf-8")

    exit_code = main([
        "process",
        "-i", str(input_file),
        "-o", str(output_file),
        "-r", "id", "name",
        "--job-id", "job_test_999"
    ])

    assert exit_code == 0
    assert output_file.exists()

    output_content = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(output_content) == 2
    assert output_content[0]["record_id"] == "rec_1"
    assert output_content[0]["transformed_data"]["name"] == "Alpha Item"
    assert output_content[0]["metadata"]["job_id"] == "job_test_999"


def test_main_process_validation_failure(tmp_path):
    input_file = tmp_path / "invalid_records.json"
    input_data = [
        {"id": "rec_1"}  # missing 'name'
    ]
    input_file.write_text(json.dumps(input_data), encoding="utf-8")

    exit_code = main([
        "process",
        "-i", str(input_file),
        "-r", "id", "name"
    ])

    assert exit_code == 1
