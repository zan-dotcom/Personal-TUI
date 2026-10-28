"""Responsive plain-text dashboard panels."""

from datetime import datetime
import shutil
import textwrap


def panel(title, lines, width):
    inner = width - 4
    rows = []
    for line in lines:
        clean = ''.join(c if c.isprintable() else ' ' for c in str(line))
        rows.extend(textwrap.wrap(clean, width=inner, replace_whitespace=False) or [''])
    label = f' {title} '
    return ['+' + label[:width - 2].ljust(width - 2, '-') + '+',
            *['| ' + row.ljust(inner) + ' |' for row in rows],
            '+' + '-' * (width - 2) + '+']


def dashboard(sections, width=None):
    width = max(24, min(width or shutil.get_terminal_size((100, 30)).columns, 120))
    lines = ['PERSONAL TUI  /  DASHBOARD', datetime.now().astimezone().strftime('%a %d %b %Y  %H:%M:%S %Z'), '']
    if width < 90:
        for title, body in sections:
            lines.extend(panel(title, body, width))
    else:
        left_width = (width - 2) // 2
        right_width = width - left_width - 2
        for index in range(0, len(sections), 2):
            left = panel(*sections[index], left_width)
            right = panel(*sections[index + 1], right_width) if index + 1 < len(sections) else []
            for row in range(max(len(left), len(right))):
                lines.append((left[row] if row < len(left) else ' ' * left_width) + '  ' + (right[row] if row < len(right) else ''))
    return '\n'.join(lines)
