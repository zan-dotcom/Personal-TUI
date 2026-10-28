# Personal TUI

A lightweight terminal dashboard for tasks and notes, built with Python's standard
library. Requires Python 3.10 or newer; no dependency installation is needed.

## Run

From the repository directory:

```sh
python3 -m personal_tui
```

Type `help` for commands. Use `add Buy groceries`, `done 1`, and `note An idea`
to get started. `done` toggles completion; `delete` removes a task and `unnote`
removes a note. Type `quit` to exit. Numbers refer to the displayed list.

Data is saved after every change to
`$XDG_DATA_HOME/personal-tui/data.json` (default: `~/.local/share/personal-tui/data.json`).
Writes replace the file atomically. Invalid data is reported without overwriting it.
Use one running instance per data file to avoid conflicting updates.

For scripts or a custom data file:

```sh
python3 -m personal_tui --data /tmp/my-dashboard.json --command 'add First task'
python3 -m personal_tui --data /tmp/my-dashboard.json --command list
```

## Test

```sh
python3 -m unittest discover -s tests -v
```

The project needs no API keys, database server, or network access at runtime.
