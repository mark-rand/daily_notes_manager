from note_manager import get_files, process_notes, process_args
from note_data_structures import Note
import os
from unittest import mock


def test_process_args_checks_for_notes_home(capsys):
    process_args([])
    captured = capsys.readouterr()
    output = captured.out
    assert output == "Usage: python note_manager.py <notes_home>\n"


import pytest


def test_process_args_with_invalid_directory():
    with pytest.raises(ValueError, match="invalid directory: 'invalid_directory'"):
        process_args(["note_manager.py", "invalid_directory"])


def test_process_args_with_valid_unwritable_directory(capsys):
    with mock.patch.object(os.path, "isdir", return_value=True):
        with mock.patch.object(os, "access", return_value=False):
            with pytest.raises(
                ValueError,
                match="no write access to directory: '/doesnt/matter/for/test'",
            ):
                process_args(["note_manager.py", "/doesnt/matter/for/test"])


def test_process_args_with_valid_directory(capsys):
    with mock.patch.object(os.path, "isdir", return_value=True):
        with mock.patch.object(os, "access", return_value=True):
            notes_home = process_args(["note_manager.py", "/doesnt/matter/for/test"])
    captured = capsys.readouterr()
    output = captured.out
    assert output == "Processing home directory: /doesnt/matter/for/test\n"
    assert notes_home == "/doesnt/matter/for/test"


def test_process_directory_gets_config():
    with mock.patch.object(os.path, "isfile", return_value=False):
        with pytest.raises(
            FileNotFoundError, match="Config file not found or inaccessible: '/doesnt/matter/for/test/config.md'"
        ):
            get_files("/doesnt/matter/for/test")
        with mock.patch.object(os.path, "isfile", return_value=True):
            with mock.patch.object(os.path, "exists", return_value=True):
                with mock.patch.object(os, "access", return_value=True):
                    with mock.patch.object(os, "listdir", return_value=['123.md', '2025-01-01.md']):
                        config_file, other_files = get_files("/doesnt/matter/for/test")
                        assert config_file == "/doesnt/matter/for/test/config.md"
                        assert other_files == ['2025-01-01.md']


def test_accepts_list_of_note_files():
    note1 = Note()
    notes_to_write = process_notes([note1])
    assert isinstance(notes_to_write, list)
