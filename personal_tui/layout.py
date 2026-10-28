"""Responsive Nord-inspired terminal panels with optional true-color styling."""

from datetime import datetime
import os
import re
import shutil
import sys
import textwrap

NORD = {
    'background': '46;52;64',
    'text': '216;222;233',
    'muted': '129;161;193',
    'frost': '136;192;208',
    'green': '163;190;140',
    'yellow': '235;203;139',
    'red': '191;97;106',
}


def panel(title, lines, width, height=0):
    inner = width - 4
    rows = []
    for line in lines:
        clean = ''.join(c if c.isprintable() else ' ' for c in str(line))
        rows.extend(textwrap.wrap(clean, width=inner, replace_whitespace=False) or [''])
    rows.extend([''] * max(0, height - len(rows)))
    label = f' {title} '
    return ['╭─' + label[:width - 4].ljust(width - 4, '─') + '─╮',
            *['│ ' + row.ljust(inner) + ' │' for row in rows],
            '╰' + '─' * (width - 2) + '╯']


def colorize(line):
    """Style only generated layout text; input controls are stripped by panel()."""
    def paint(text, role):
        return f'\033[38;2;{NORD[role]}m{text}\033[38;2;{NORD["text"]}m'
    line = re.sub(r'[╭╮╰╯│─]', lambda m: paint(m[0], 'muted'), line)
    line = re.sub(r'█+', lambda m: paint(m[0], 'frost'), line)
    line = re.sub(r'░+', lambda m: paint(m[0], 'muted'), line)
    line = re.sub(r'\b\d+(?:\.\d+)?%', lambda m: paint(m[0], 'red' if float(m[0][:-1]) >= 90 else 'yellow' if float(m[0][:-1]) >= 70 else 'green'), line)
    line = re.sub(r'\b(?:SYSTEM|WEATHER|STORAGE|TASKS|NOTES|CONTROLS)\b', lambda m: paint(m[0], 'frost'), line)
    return f'\033[48;2;{NORD["background"]}m\033[38;2;{NORD["text"]}m{line}\033[0m'


def dashboard(sections, width=None, color=None):
    width = max(24, min(width or shutil.get_terminal_size((100, 30)).columns, 120))
    color = (sys.stdout.isatty() and 'NO_COLOR' not in os.environ and os.environ.get('TERM') != 'dumb') if color is None else color
    stamp = datetime.now().astimezone().strftime('%d %b %Y · %H:%M:%S %Z')
    lines = ['  PERSONAL TUI  /  NORD', '  ' + stamp, '']
    if width < 90:
        for title, body in sections:
            lines.extend(panel(title, body, width, height=3))
            lines.append('')
    else:
        left_width = (width - 2) // 2
        right_width = width - left_width - 2
        for index in range(0, len(sections), 2):
            left = panel(*sections[index], left_width, height=3)
            right = panel(*sections[index + 1], right_width, height=3) if index + 1 < len(sections) else []
            height = max(len(left), len(right)) - 2
            left = panel(*sections[index], left_width, height=height)
            if right:
                right = panel(*sections[index + 1], right_width, height=height)
            for row in range(len(left)):
                lines.append(left[row] + '  ' + (right[row] if right else ' ' * right_width))
            lines.append('')
    lines = [line[:width].ljust(width) for line in lines]
    return '\n'.join(colorize(line) if color else line for line in lines)
