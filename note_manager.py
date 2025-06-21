#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script processes the notes in a specified directory.
"""

import sys
import os
import re
from note_data_structures import Note


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


if __name__ == "__main__":
    notes_home = process_args(sys.argv)
    if notes_home:
        config_file, note_files = get_files(notes_home)
