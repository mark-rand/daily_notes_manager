from dataclasses import dataclass


@dataclass
class NoteManagerConfig:
    """
    Configuration for the NoteManager.
    Will contain the configuration as parsed in the note manager
    """

    task_list_for_day: list[tuple[list[str], str]]
    sections: list[tuple[str, str]]


@dataclass
class Note:
    """
    Represents a note with a title and content.

    Attributes:
        title (str): The title of the note.
        content (str): The content of the note.
    """

    title: str = ""
    content: str = ""
