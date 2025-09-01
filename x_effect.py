"""
Module for processing x effect files.
"""

import os
import re
from note_manager import get_days_for_pattern
from datetime import datetime
from datetime import date


def check_x_effect_file(file_path):
    """Check if the x effect file exists."""
    if not os.path.exists(file_path):
        raise ValueError("X effect file does not exist")


def count_columns_in_table(line: str) -> int:
    """Count the number of columns in a markdown table line."""
    return line.strip().count("|") - 1


def process_x_effect_file(file_path):
    """
    Process the x effect file.
    Open the file
    Find a table
    Add the next week's dates to the table
    """
    with open(file_path, "r+", encoding="utf-8") as file:
        content = file.readlines()
        first_date: int = -1
        date_on_line: str = ""
        column_count: int = 0
        for i, line in enumerate(content):
            line = line.strip()
            match = re.match(r"^\|\s+(\d{4}-\d{2}-\d{2})", line)
            if match:
                first_date = i - 1
                date_on_line = match.group(1)
                column_count = count_columns_in_table(line)
                break

        if first_date == -1:
            raise ValueError("No table found")

        file.seek(0)
        date_as_date: date = datetime.strptime(date_on_line, "%Y-%m-%d").date()
        new_date_cols = ""
        dates = list(reversed(get_days_for_pattern("*", date_as_date)))
        dates.pop()
        for this_date in dates:
            new_date_cols += f"| {this_date} {'|  <input type="checkbox"/> ' * (column_count - 1)}|\n"
        content.insert(first_date + 1, new_date_cols)
        file.write("".join(content))


def main(file_path):
    """Main function to process the x effect file."""
    check_x_effect_file(file_path)
    process_x_effect_file(file_path)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python x_effect.py <x_effect_file_path>")
        sys.exit(1)

    x_effect_file_path = sys.argv[1]
    main(x_effect_file_path)