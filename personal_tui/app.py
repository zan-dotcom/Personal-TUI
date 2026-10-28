"""Dependency-free terminal dashboard with persistent tasks and notes."""

import argparse
import json
import os
from pathlib import Path
import tempfile


def load(path):
    if not path.exists():
        return {"tasks": [], "notes": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(
        isinstance(data.get(key), list) for key in ("tasks", "notes")
    ):
        raise ValueError("Expected tasks and notes lists")
    if not all(
        isinstance(task, dict)
        and isinstance(task.get("text"), str)
        and isinstance(task.get("done"), bool)
        for task in data["tasks"]
    ) or not all(isinstance(note, str) for note in data["notes"]):
        raise ValueError("Invalid task or note data")
    return data


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def render(data):
    lines = ["PERSONAL TUI", "============", "", "Tasks"]
    for index, task in enumerate(data["tasks"], 1):
        mark = "x" if task["done"] else " "
        lines.append(f"  {index}. [{mark}] {task['text']}")
    if not data["tasks"]:
        lines.append("  No tasks yet. Add one with: add Your task")
    lines.extend(["", "Notes"])
    lines.extend(f"  {i}. {note}" for i, note in enumerate(data["notes"], 1))
    if not data["notes"]:
        lines.append("  No notes yet. Add one with: note Your note")
    return "\n".join(lines)


def apply(data, command):
    """Apply a command and return whether it changed stored data."""
    verb, _, argument = command.strip().partition(" ")
    argument = argument.strip()
    if verb in ("add", "note"):
        if not argument:
            raise ValueError(f"Usage: {verb} <text>")
        if verb == "add":
            data["tasks"].append({"text": argument, "done": False})
        else:
            data["notes"].append(argument)
        return True
    if verb in ("done", "delete", "unnote"):
        key = "notes" if verb == "unnote" else "tasks"
        try:
            index = int(argument) - 1
        except ValueError:
            raise ValueError(f"Usage: {verb} <number>") from None
        if not 0 <= index < len(data[key]):
            raise ValueError("That number does not exist")
        if verb == "done":
            data[key][index]["done"] = not data[key][index]["done"]
        else:
            del data[key][index]
        return True
    if verb in ("", "list"):
        return False
    raise ValueError("Unknown command. Type help for commands.")


HELP = """Commands:
  add <text>     Add a task
  done <number>  Toggle task completion
  delete <number> Delete a task
  note <text>    Add a note
  unnote <number> Delete a note
  list           Show dashboard
  help           Show commands
  quit           Exit
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    parser.add_argument("--data", type=Path, default=default / "personal-tui/data.json")
    parser.add_argument("--command", help="Run one command and exit")
    args = parser.parse_args()
    try:
        data = load(args.data)
        if args.command is not None:
            if args.command.strip() == "help":
                print(HELP)
                return
            if apply(data, args.command):
                save(args.data, data)
            print(render(data))
            return
        print(render(data))
        print("\nType help for commands; quit to exit.")
        while True:
            try:
                command = input("\npersonal> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if command in ("quit", "exit"):
                return
            if command == "help":
                print(HELP)
                continue
            try:
                if apply(data, command):
                    save(args.data, data)
                print(render(data))
            except ValueError as error:
                print(f"Error: {error}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")
