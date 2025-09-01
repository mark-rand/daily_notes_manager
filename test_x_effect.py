"""
This tests the x effect script which will open the x effect file
and ensure that there are plenty of dates available for the next week.
"""

import os
from unittest import mock
import pytest
import x_effect


def test_x_effect_creates_error_if_file_doesnt_exist():
    """Test that an error is raised if the x effect file does not exist."""
    with mock.patch.object(os.path, "exists", return_value=False):
        with pytest.raises(ValueError, match="X effect file does not exist"):
            x_effect.check_x_effect_file("non_existent_file.txt")


def test_x_effect_main_calls_functions():
    """Test that the main function calls the necessary functions."""
    with mock.patch.object(x_effect, "check_x_effect_file") as mock_check:
        with mock.patch.object(x_effect, "process_x_effect_file") as mock_process:
            x_effect.main("some_file.txt")
            mock_process.assert_called_once_with("some_file.txt")
            mock_check.assert_called_once_with("some_file.txt")


def test_process_x_effect_file_processing_no_table():
    """Test that process_x_effect_file handles a file with no table."""
    with mock.patch("builtins.open", mock.mock_open(read_data="No table here")):
        with pytest.raises(ValueError, match="No table found"):
            x_effect.process_x_effect_file("dummy_file.txt")


def test_count_columns_in_table():
    """Test that the number of columns in a table is counted correctly."""
    sample_lines = {
        "| Date       | Task        |": 2,
        "| Date | Task | Extra |": 3,
        "| SingleColumn |": 1,
        "| Lots of | Columns | Here | Now |": 4,
    }
    for line, expected_count in sample_lines.items():
        assert x_effect.count_columns_in_table(line) == expected_count

def test_reverse_pattern_days():
    """Test that get_days_for_pattern returns dates in reverse order."""
    from note_manager import get_days_for_pattern
    from datetime import datetime

    start_date = datetime.strptime("2024-06-01", "%Y-%m-%d").date()
    days = list(reversed(get_days_for_pattern("*", start_date)))
    days.pop()
    assert len(days) == 6
    assert days[0] == "2024-06-07"
    assert days[1] == "2024-06-06"
    assert days[2] == "2024-06-05"
    assert days[5] == "2024-06-02"

def test_process_x_effect_file_processing_with_table():
    """Test that process_x_effect_file processes a file with a table."""
    file_content = """
Some header text
| Date       | Task        |
|------------|-------------|
| 2024-06-02 | Task 1      |
| 2024-06-01 | Task 2      |
Some footer text
"""
    with mock.patch(
        "builtins.open", mock.mock_open(read_data=file_content)
    ) as mock_open:
        x_effect.process_x_effect_file("dummy_file.txt")
        mock_open.assert_called_once_with("dummy_file.txt", "r+", encoding="utf-8")
        mock_open.return_value.readlines.assert_called_once()
        mock_open.return_value.seek.assert_called_once_with(0)
        mock_open.return_value.write.assert_any_call("""
Some header text
| Date       | Task        |
|------------|-------------|
| 2024-06-08 |  <input type="checkbox"/> |
| 2024-06-07 |  <input type="checkbox"/> |
| 2024-06-06 |  <input type="checkbox"/> |
| 2024-06-05 |  <input type="checkbox"/> |
| 2024-06-04 |  <input type="checkbox"/> |
| 2024-06-03 |  <input type="checkbox"/> |
| 2024-06-02 | Task 1      |
| 2024-06-01 | Task 2      |
Some footer text
""")
