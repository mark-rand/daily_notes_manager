from dataclasses import dataclass


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
