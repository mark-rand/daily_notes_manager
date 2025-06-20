# daily_notes_manager
Manages your daily notes files (specifically for Obsidian)

The notes manager should be run every day it will:
* Open and process the config.md file
* Process all files from before today's date, and archive them so we know that they're processed
** Any tasks that have not been completed will be moved to the current day's file
* Generate files for the next 7 days
** Add specific entries for single days of the week and every day

