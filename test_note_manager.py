"""
Test cases for the note_manager module.
"""

from datetime import date
import os
from unittest import mock
import pytest
import note_manager
from note_manager import get_files, parse_config, process_notes, process_args
from note_data_structures import Note, NoteManagerConfig


def test_process_args_checks_for_notes_home(capsys):
    """
    Test that process_args prints usage message when no notes_home is provided.
    """
    process_args([])
    captured = capsys.readouterr()
    output = captured.out
    assert output == "Usage: python note_manager.py <notes_home>\n"


def test_process_args_with_invalid_directory():
    """
    Test that process_args raises ValueError when an invalid directory is provided.
    """
    with pytest.raises(ValueError, match="invalid directory: 'invalid_directory'"):
        process_args(["note_manager.py", "invalid_directory"])


def test_process_args_with_valid_unwritable_directory():
    """
    Test that process_args raises ValueError when the directory is not writable.
    """
    with mock.patch.object(os.path, "isdir", return_value=True):
        with mock.patch.object(os, "access", return_value=False):
            with pytest.raises(
                ValueError,
                match="no write access to directory: '/doesnt/matter/for/test'",
            ):
                process_args(["note_manager.py", "/doesnt/matter/for/test"])


def test_process_args_with_valid_directory(capsys):
    """
    Test that process_args processes a valid directory and prints the home directory.
    """
    with mock.patch.object(os.path, "isdir", return_value=True):
        with mock.patch.object(os, "access", return_value=True):
            notes_home = process_args(["note_manager.py", "/doesnt/matter/for/test"])
    captured = capsys.readouterr()
    output = captured.out
    assert output == "Processing home directory: /doesnt/matter/for/test\n"
    assert notes_home == "/doesnt/matter/for/test"


def test_process_directory_gets_config():
    """
    Test that get_files retrieves the config file and other files correctly.
    """
    with mock.patch.object(os.path, "isfile", return_value=False):
        with pytest.raises(
            FileNotFoundError,
            match="Config file not found or inaccessible: '/doesnt/matter/for/test/config.md'",
        ):
            get_files("/doesnt/matter/for/test")
        with mock.patch.object(os.path, "isfile", return_value=True):
            with mock.patch.object(os.path, "exists", return_value=True):
                with mock.patch.object(os, "access", return_value=True):
                    with mock.patch.object(
                        os, "listdir", return_value=["123.md", "2025-01-01.md"]
                    ):
                        config_file, other_files = get_files("/doesnt/matter/for/test")
                        assert config_file == "/doesnt/matter/for/test/config.md"
                        assert other_files == ["2025-01-01.md"]


def test_get_days_for_pattern():
    """
    Test that get_days_for_pattern returns the correct days for a given pattern.
    """
    first_january = date(2025, 1, 1)  # Wednesday 1st January 2025
    all_week = [
        "2025-01-01",
        "2025-01-02",
        "2025-01-03",
        "2025-01-04",
        "2025-01-05",
        "2025-01-06",
        "2025-01-07",
    ]
    assert note_manager.get_days_for_pattern("", first_january) == all_week
    assert note_manager.get_days_for_pattern("*", first_january) == all_week
    assert note_manager.get_days_for_pattern("", date(2025, 1, 31)) == [
        "2025-01-31",
        "2025-02-01",
        "2025-02-02",
        "2025-02-03",
        "2025-02-04",
        "2025-02-05",
        "2025-02-06",
    ]
    assert note_manager.get_days_for_pattern("", date(2025, 12, 23)) == [
        "2025-12-23",
        "2025-12-24",
        "2025-12-25",
        "2025-12-26",
        "2025-12-27",
        "2025-12-28",
        "2025-12-29",
    ]
    assert note_manager.get_days_for_pattern("31", date(2025, 1, 31)) == ["2025-01-31"]
    assert note_manager.get_days_for_pattern("31", date(2025, 12, 25)) == ["2025-12-31"]
    assert note_manager.get_days_for_pattern("31", date(2025, 12, 23)) == []
    assert note_manager.get_days_for_pattern("01", date(2025, 12, 26)) == ["2026-01-01"]
    assert note_manager.get_days_for_pattern("1231", first_january) == []
    assert note_manager.get_days_for_pattern("0101,mon,26", first_january) == [
        "2025-01-01",
        "2025-01-06",
    ]
    assert note_manager.get_days_for_pattern("1225", date(2025, 12, 25)) == [
        "2025-12-25"
    ]
    assert note_manager.get_days_for_pattern("1225", date(2025, 12, 24)) == [
        "2025-12-25"
    ]
    assert note_manager.get_days_for_pattern("1225", first_january) == []
    assert note_manager.get_days_for_pattern("20250102,0101", first_january) == [
        "2025-01-01",
        "2025-01-02",
    ]
    assert note_manager.get_days_for_pattern(
        "sat,21,0621,mon,wed", date(2025, 6, 21)
    ) == ["2025-06-21", "2025-06-23", "2025-06-25"]


def test_config_parsing():
    """
    Test that the config file is parsed correctly.
    """
    sample_config = """
# Diary
Write about my day here
# Another section
Write something else here
# Tasks
mon:Put out the: bins
*:Walk the dog
    """
    with mock.patch("builtins.open", mock.mock_open(read_data=sample_config)):
        parsed_config: NoteManagerConfig = parse_config(
            "config_file.md", date(2025, 2, 28)  # A Friday
        )
        assert isinstance(parsed_config, NoteManagerConfig)
        assert parsed_config.task_list_for_day == [
            (
                ["2025-03-03"],
                "Put out the: bins",
            ),
            (
                [
                    "2025-02-28",
                    "2025-03-01",
                    "2025-03-02",
                    "2025-03-03",
                    "2025-03-04",
                    "2025-03-05",
                    "2025-03-06",
                ],
                "Walk the dog",
            ),
        ]
        assert parsed_config.sections == [
            ("# Diary", "Write about my day here"),
            ("# Another section", "Write something else here"),
            ("# Tasks", ""),
        ]

def test_output_tasks_for_day():
    """
    Test that the output of tasks for a specific day is correct.
    """
    sample_config = NoteManagerConfig(
        task_list_for_day=[
            (["2025-01-01"], "Task 1"),
            (["2025-01-02"], "Task 2"),
            (["2025-01-01", "2025-01-31"], "Task 3"),
        ],
        sections=[],
    )
    tasks = note_manager.output_tasks_for_day(sample_config, "2025-01-01")
    assert tasks == ["[ ] Task 1", "[ ] Task 3"]

def test_archive_and_backup_directories_exist():
    """
    Test that the archive and backup directories are created if they do not exist.
    """
    BASE_DIR = "/doesnt/matter/for/test"
    with mock.patch("os.path.exists", return_value=False):
        with mock.patch("os.makedirs") as mock_makedirs:
            note_manager.directory_check(BASE_DIR)
            assert mock_makedirs.call_count == 2
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch("os.makedirs") as mock_makedirs:
            note_manager.directory_check(BASE_DIR)
            mock_makedirs.assert_not_called()


def test_process_single_file_before_archiving():
    """
    The notes manager processes a file then writes the filtered version to the archive
    directory. 
    """
    note_file = "2025-01-01.md"
    contents_before_processing = """
# Title
Content
#thoughtoftheday (delete_if_not_entered)
# Tasks
- [ ] Task 1
- [x] Task 2
* [ ] Task 3
"""
    with mock.patch("builtins.open") as mock_file_open:
        write_mock_return_value = mock.mock_open().return_value
        mock_file_open.side_effect = [
            mock.mock_open(read_data=contents_before_processing).return_value,
            write_mock_return_value,
        ]
        incomplete_tasks: set[str] = note_manager.process_single_file_before_archiving(note_file, "/doesnt/matter/for/test/")
        assert mock_file_open.call_count == 2
        assert mock_file_open.call_args_list[0][0] == (
            os.path.join("/doesnt/matter/for/test", note_file), "r"
        )
        assert mock_file_open.call_args_list[0][1] == {"encoding": "utf-8"}
        assert incomplete_tasks == {"Task 1", "Task 3"}
        assert len(mock_file_open.mock_calls) == 2
        assert write_mock_return_value.write.call_count == 1
        assert write_mock_return_value.write.call_args[0][0] == """
# Title
Content
# Tasks
- [ ] Task 1
- [x] Task 2
* [ ] Task 3
"""


def test_process_old_notes():
    """
    We want to go through the old notes, delete any unused lines and gather up
    and tasks which have not been completed.
    """
    note_files = [
        "2025-01-01.md",
        "2025-01-02.md",
        "2025-01-03.md",
        "2025-01-04.md",
    ]
    with mock.patch("os.rename") as mock_rename:
        with mock.patch("note_manager.process_single_file_before_archiving") as mock_process_single_file:
            note_manager.process_old(note_files, "/doesnt/matter/for/test", date(2025, 1, 3))
            assert mock_rename.call_count == 2
            assert mock_rename.call_args_list[0][0][0] == os.path.join("/doesnt/matter/for/test", "2025-01-01.md")
            assert mock_rename.call_args_list[1][0][0] == os.path.join("/doesnt/matter/for/test", "2025-01-02.md")
            assert mock_process_single_file.call_count == 2


def test_accepts_list_of_note_files():
    note1 = Note()
    notes_to_write = process_notes([note1])
    assert isinstance(notes_to_write, list)
