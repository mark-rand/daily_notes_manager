#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script processes the notes in a specified directory.
"""

from datetime import date, timedelta
from enum import StrEnum, auto
import sys
import os
import re
from note_data_structures import Note, NoteManagerConfig

ARCHIVE_HOME = "archive"
BACKUP_HOME = "backup"


class CurrentSection(StrEnum):
    """
    Enum to represent the current section of the note while being processed.
    """

    TASKS = auto()
    OTHER = auto()


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
    Tasks work like this: the config will hold each task and the dates that
    it is relevant for (in YYYY-MM-DD format).
    The criteria for a task can be any of these in a comma-separated list:
    * / blank - No specific date (every day)
    MMDD - relevant for the month and day, regardless of the year
    DD - relevant for the day of the month, regardless of the month and year
    mon, tue, wed, thu, fri, sat, sun (case insensitive) - relevant for the day of the week
    """
    all_week_as_string = [
        dd.strftime("%Y-%m-%d")
        for dd in [today_date + timedelta(days=i) for i in range(7)]
    ]
    if not pattern or pattern == "*":
        return all_week_as_string
    matched_days: set[str] = set()
    for sub_pattern in pattern.split(","):
        sub_pattern = sub_pattern.strip().lower()
        if re.match(r"^\d{8}$", sub_pattern):
            formatted_pattern = (
                f"{sub_pattern[:4]}-{sub_pattern[4:6]}-{sub_pattern[6:]}"
            )
            matched_days.update(
                [d for d in all_week_as_string if d == formatted_pattern]
            )
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
    with open(config_file_location, "r", encoding="utf-8") as file:
        current_section = CurrentSection.OTHER
        sections: list[tuple[str, str]] = []
        current_section_name = ""
        current_section_content = []
        processed_first_section = False
        for line in file:
            line = line.strip() if line else ""
            if line:
                if line.startswith("#"):
                    if processed_first_section:
                        sections.append(
                            (current_section_name, "\n".join(current_section_content))
                        )
                    else:
                        processed_first_section = True
                    current_section_name = line
                    current_section_content = []
                    current_section = CurrentSection.OTHER
                    if current_section_name.lower().find("tasks") != -1:
                        current_section = CurrentSection.TASKS
                else:
                    if current_section == CurrentSection.OTHER:
                        current_section_content.append(line)
                    elif current_section == CurrentSection.TASKS:
                        # Process task lines
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            date_pattern, task = parts[0].strip(), parts[1].strip()
                        else:
                            date_pattern, task = "", line
                        task_list_for_day.append(
                            (get_days_for_pattern(date_pattern, today_date), task)
                        )
    sections.append((current_section_name, "\n".join(current_section_content)))
    config: NoteManagerConfig = NoteManagerConfig(task_list_for_day, sections)
    return config


def output_tasks_for_day(config: NoteManagerConfig, day: str) -> list[str]:
    """
    Outputs the tasks for a specific day based on the configuration.

    Args:
        config (NoteManagerConfig): The configuration object.
        day (str): The day in YYYY-MM-DD format.

    Returns:
        list[str]: A list of tasks for the specified day.
    """
    tasks_for_day = []
    for task_dates, task in config.task_list_for_day:
        if day in task_dates:
            tasks_for_day.append("[ ] " + task)
    return tasks_for_day


def directory_check(notes_home: str) -> None:
    """
    Checks if the archive and backup directorys exist and creates them if not.

    Args:
        notes_home (str): The path to the notes home directory.
    """
    for subdir in [ARCHIVE_HOME, BACKUP_HOME]:
        subdir_path = os.path.join(notes_home, subdir)
        if not os.path.exists(subdir_path):
            print(f"Creating directory: {subdir_path}")
            os.makedirs(subdir_path)


def process_single_file_before_archiving(note_file: str, notes_home: str) -> set[str]:
    """
    Processes a single note file before archiving it.
    Returns:
        set[str]: A set of tasks that have not been completed.
    """
    print(f"Processing file: {note_file} before archiving")
    incomplete_tasks: set[str] = set()
    new_lines = []
    with open(os.path.join(notes_home, note_file), "r", encoding="utf-8") as file:
        for line in file:
            if line.strip().endswith("(delete_if_not_entered)"):
                continue
            new_lines.append(line)
            line = line.strip()
            match = re.match(r"^(\*|-)\s\[\s\]\s(.+)", line)
            if match:
                task = match.group(2).strip()
                incomplete_tasks.add(task)
            elif re.match(r"^(\*|-)\s\[x\]\s", line, re.IGNORECASE):
                continue
    with open(
        os.path.join(notes_home, ARCHIVE_HOME, note_file), "w", encoding="utf-8"
    ) as archive_file:
        print(f"Archiving {note_file} to {os.path.join(notes_home, ARCHIVE_HOME)}")
        archive_file.write("".join(new_lines))
    return incomplete_tasks


def process_old(
    note_files: list[str],
    notes_home: str,
    today_date: date,
) -> set[str]:
    """
    Processes old notes, deleting unused lines and gathering tasks that have not been completed.

    Args:
        note_files (list[str]): List of note files to process.
        notes_home (str): The path to the notes home directory.
        today_date (date): Today's date as a datetime.date object.

    """
    incomplete_tasks: set[str] = set()
    todays_date_str = today_date.strftime("%Y-%m-%d")
    for note_file in note_files:
        if note_file < todays_date_str:
            file_path = os.path.join(notes_home, note_file)
            try:
                incomplete_tasks.update(process_single_file_before_archiving(note_file, notes_home))
                os.rename(
                    file_path,
                    os.path.join(notes_home, BACKUP_HOME, note_file)
                )
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error processing file {note_file}: {e}")
                sys.exit(1)
    return incomplete_tasks


def main() -> None:
    """
    Main function to run the note manager.
    """
    notes_home = process_args(sys.argv)
    if notes_home:
        config_file, note_files = get_files(notes_home)
        parsed_config: NoteManagerConfig = parse_config(config_file, date.today())
        print(f"Parsed configuration: {parsed_config}")
        directory_check(notes_home)
        incomplete_tasks: set[str] = process_old(note_files, notes_home, date.today())


if __name__ == "__main__":
    main()
