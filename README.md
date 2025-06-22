# daily_notes_manager
Manages your daily notes files (specifically for Obsidian)

The notes manager should be run every day it will:
* Open and process the config.md file
* Process all files from before today's date, and archive them so we know that they're processed
** Any tasks that have not been completed will be moved to an "outstanding tasks" file
** Delete any lines which contain "delete_if_not_entered" - this allows you do have journal prompts or hashtags, for example, which aren't mandatory and will be filtered out
* Generate files for the next 7 days - show number of outstanding tasks
** Add specific entries for single days of the week and every day

## Limitations
Sections don't have any hierachy - I'm not too bothered about that!
