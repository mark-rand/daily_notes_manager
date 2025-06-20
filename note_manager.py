#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script processes the notes in a specified directory.
"""

from note_data_structures import Note
import sys
import os
import re


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


def process_args(command_line_args: list[str]) -> None:
    """
    Main function to process notes in the specified directory.
    """
    if len(command_line_args) < 2:
        print("Usage: python note_manager.py <notes_home>")
        return

    notes_home = command_line_args[1]
    if not os.path.isdir(notes_home):
        raise ValueError(f"invalid directory: '{notes_home}'")
    if not os.access(notes_home, os.W_OK):
        raise ValueError(f"no write access to directory: '{notes_home}'")
    print(f"Processing home directory: {notes_home}")
    return notes_home


def get_files(notes_home: str) -> tuple[str, list[str]]:
    """
    Gets the configuration file and other files in the notes home directory.
    """
    config_file = os.path.join(notes_home, "config.md")
    if (
        not os.path.isfile(config_file)
        or not os.path.exists(config_file)
        or not os.access(config_file, os.R_OK)
    ):
        raise FileNotFoundError(
            f"Config file not found or inaccessible: '{config_file}'"
        )
    other_files = [
        f for f in os.listdir(notes_home) if re.match(r"\d{4}-\d{2}-\d{2}\.md$", f)
    ]
    return config_file, other_files


if __name__ == "__main__":
    notes_home = process_args(sys.argv)
    config_file, other_files = get_files(notes_home)
