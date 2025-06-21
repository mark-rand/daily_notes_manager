#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script processes the notes in a specified directory.
"""

import sys
import os
import re
from note_data_structures import Note, NoteManagerConfig
from datetime import date, timedelta


def process_notes(notes: list[Note]) -> list[Note]:
    """
    Processes a list of Note objects and returns a list of notes to write.

    Args:
        notes (list): A list of Note objects.

    Returns:
        list: A list of notes to write.
    """
    # Assuming Note has a method to get the content or representation
    return [note for note in notes if isinstance(note, Note)]


def process_args(command_line_args: list[str]) -> str | None:
    """
    Main function to process notes in the specified directory.
    """
    if len(command_line_args) < 2:
        print("Usage: python note_manager.py <notes_home>")
        return

    notes_dir = command_line_args[1]
    if not os.path.isdir(notes_dir):
        raise ValueError(f"invalid directory: '{notes_dir}'")
    if not os.access(notes_dir, os.W_OK):
        raise ValueError(f"no write access to directory: '{notes_dir}'")
    print(f"Processing home directory: {notes_dir}")
    return notes_dir


def get_files(notes_directory: str) -> tuple[str, list[str]]:
    """
    Gets the configuration file and other files in the notes home directory.
    """
    config_path = os.path.join(notes_directory, "config.md")
    if (
        not os.path.isfile(config_path)
        or not os.path.exists(config_path)
        or not os.access(config_path, os.R_OK)
    ):
        raise FileNotFoundError(
            f"Config file not found or inaccessible: '{config_path}'"
        )
    filtered_note_files = [
        f for f in os.listdir(notes_directory) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", f)
    ]
    return config_path, filtered_note_files


def get_days_for_pattern(pattern: str, today_date: date) -> list[str]:
    """
    Returns a list of dates in YYYY-MM-DD format for the given pattern.
    """
    all_week_as_string = [
        dd.strftime("%Y-%m-%d")
        for dd in [today_date + timedelta(days=i) for i in range(7)]
    ]
    if not pattern or pattern == "*":
        # All days by default
        return all_week_as_string
    matched_days: set[str] = set()
    for sub_pattern in pattern.split(","):
        sub_pattern = sub_pattern.strip().lower()
        if re.match(r"^\d{8}$", sub_pattern):
            formatted_pattern = f"{sub_pattern[:4]}-{sub_pattern[4:6]}-{sub_pattern[6:]}"
            matched_days.update([d for d in all_week_as_string if d == formatted_pattern])
        elif re.match(r"^\d{2}$", sub_pattern):
            # Day of the month
            matched_days.update(
                [d for d in all_week_as_string if d[-2:] == sub_pattern]
            )
        elif re.match(r"^\d{2}\d{2}$", sub_pattern):
            as_string = f"{sub_pattern[:2]}-{sub_pattern[2:]}"
            matched_days.update([d for d in all_week_as_string if d[5:] == as_string])
        elif sub_pattern in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
            for day in all_week_as_string:
                as_dow = date.fromisoformat(day).strftime("%a").lower()
                if as_dow == sub_pattern:
                    matched_days.add(day)
    return sorted(matched_days)


def parse_config(config_file_location: str, today_date: date) -> NoteManagerConfig:
    """
    Parses the configuration file and returns a NoteManagerConfig object.

    Args:
        config_file_location (str): Path to the config file.
        today_date (date): Today's date as a datetime.date object.

    Returns:
        NoteManagerConfig: The parsed configuration.
    """
    task_list_for_day: list[tuple[list[str], str]] = []
    # Tasks work like this: the config will hold each task and the dates that
    # it is relevant for (in YYYY-MM-DD format).
    # The criteria for a task can be any of these in a comma-separated list:
    # - No specific date (always relevant)
    # MMDD - relevant for the month and day, regardless of the year
    # DD - relevant for the day of the month, regardless of the month and year
    # mon, tue, wed, thu, fri, sat, sun (case insensitive) - relevant for the day of the week
    with open(config_file_location, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                task_list_for_day.append((["zzz"], line.strip()))
    config: NoteManagerConfig = NoteManagerConfig(task_list_for_day)
    return config


if __name__ == "__main__":
    notes_home = process_args(sys.argv)
    if notes_home:
        config_file, note_files = get_files(notes_home)
