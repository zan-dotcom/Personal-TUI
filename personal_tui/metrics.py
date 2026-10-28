"""Read Linux host metrics without third-party Python dependencies."""

from pathlib import Path
import shutil
import subprocess
import time


def cpu_ticks():
    values = [int(value) for value in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]]
    return sum(values), values[3] + values[4]


def cpu_percent(previous, current):
    total = current[0] - previous[0]
    idle = current[1] - previous[1]
    if total <= 0:
        return None
    return max(0.0, min(100.0, 100 * (total - idle) / total))


def memory():
    values = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        values[key] = int(value.split()[0]) * 1024
    total = values['MemTotal']
    used = total - values['MemAvailable']
    return used, total


def gpu_lines():
    if shutil.which('nvidia-smi'):
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,utilization.gpu,memory.used,memory.total',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2, check=True,
            )
            lines = []
            for row in result.stdout.splitlines():
                name, usage, used, total = [value.strip() for value in row.rsplit(',', 3)]
                lines.append(f'GPU {name}: {float(usage):.1f}% | VRAM {float(used):.0f}/{float(total):.0f} MiB')
            if lines:
                return lines
        except (OSError, subprocess.SubprocessError, ValueError):
            return ['GPU: unavailable (NVIDIA driver or metrics query failed)']
    lines = []
    for device in sorted(Path('/sys/class/drm').glob('card[0-9]*/device')):
        try:
            usage = float((device / 'gpu_busy_percent').read_text().strip())
            lines.append(f'GPU {device.parent.name}: {usage:.1f}%')
        except (OSError, ValueError):
            continue
    return lines or ['GPU: unavailable (no supported GPU exposed)']


class Monitor:
    def __init__(self, disk_path='/'):
        self.previous = None
        self.disk_path = disk_path

    def storage(self):
        try:
            total, used, free = shutil.disk_usage(self.disk_path)
            return [str(self.disk_path), bar('Used', used / total * 100),
                    f'{used / 2**30:.2f} / {total / 2**30:.2f} GiB used',
                    f'{free / 2**30:.2f} GiB free']
        except (OSError, ValueError, ZeroDivisionError):
            return [str(self.disk_path), 'Storage unavailable (path cannot be read)']

    def sample(self):
        lines = ['System usage (host-visible metrics)']
        try:
            current = cpu_ticks()
            if self.previous is None:
                self.previous = current
                time.sleep(0.1)
                current = cpu_ticks()
            usage = cpu_percent(self.previous, current)
            self.previous = current
            lines.append('CPU: warming up' if usage is None else bar('CPU', usage))
        except (OSError, ValueError, IndexError):
            lines.append('CPU: unavailable (Linux /proc/stat required)')
        try:
            used, total = memory()
            lines.append(f'{bar("RAM", 100 * used / total)} | {used / 2**30:.2f}/{total / 2**30:.2f} GiB')
        except (OSError, ValueError, KeyError, ZeroDivisionError):
            lines.append('RAM: unavailable (Linux /proc/meminfo required)')
        lines.extend(gpu_lines())
        return lines


def bar(label, percentage):
    filled = round(max(0, min(100, percentage)) / 5)
    return f'{label}: [{"#" * filled}{"-" * (20 - filled)}] {percentage:5.1f}%'
