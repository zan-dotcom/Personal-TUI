# Personal TUI

A lightweight terminal dashboard for tasks and notes, built with Python's standard
library. Requires Python 3.10 or newer; no dependency installation is needed.

The dashboard includes CPU utilization, RAM usage with used/total GiB, and GPU
utilization. Start the live view with:

```sh
python3 -m personal_tui --watch
```

The view refreshes every second; press Ctrl+C to exit. Run without `--watch`
to edit tasks and notes; metrics refresh after commands in that mode.

## Weather and storage dashboard

Panels arrange into two columns in wide terminals and stack in narrow terminals.
The Nord theme uses a polar-night background, frost-blue rounded borders, block
meters, and green/amber/red utilization indicators inspired by btop. Color is
enabled automatically in interactive terminals; redirected output stays plain.
Set `NO_COLOR=1` to disable color. A Unicode-capable terminal is recommended.
Weather shows current conditions, temperature and feels-like temperature in Celsius.
Choose your city explicitly (or set `PERSONAL_TUI_CITY`):

```sh
python3 -m personal_tui --watch --city "Kuala Lumpur" --disk /workspace
```

Weather uses HTTPS to `wttr.in`, needs no API key, and caches results for ten
minutes. Your selected location is sent to that service. Network failures display
an unavailable status; the rest of the dashboard continues working. The first
weather request can take up to three seconds. Without a city, no request is made.
Cloud environments must allow `wttr.in` in their network settings.

Storage shows used, total and free GiB for the filesystem containing `--disk`
(default `/`); it does not sum every mounted drive. CPU/GPU/RAM and storage
refresh every second in live mode. Weather includes its provider observation time.

CPU and RAM monitoring use Linux `/proc`. GPU monitoring supports NVIDIA through
`nvidia-smi` (including VRAM usage), and Linux GPUs exposing the DRM
`gpu_busy_percent` interface. Missing hardware, drivers, or unsupported metrics
are displayed as unavailable. No GPU tooling is installed automatically.
Cloud containers show the host metrics exposed to them, which can differ from
container resource limits. These metrics describe the machine running the app,
not the computer you use to connect to it.

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

The project needs no API keys or database server. Only optional weather requires
network access.
