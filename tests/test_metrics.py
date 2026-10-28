import subprocess
import unittest
from unittest.mock import patch

from personal_tui.metrics import Monitor, cpu_percent, gpu_lines, memory


class MetricsTests(unittest.TestCase):
    def test_cpu_uses_interval_and_counts_iowait_as_idle(self):
        self.assertEqual(cpu_percent((100, 40), (200, 65)), 75)
        self.assertIsNone(cpu_percent((100, 40), (100, 40)))

    def test_memory_uses_available_memory(self):
        with patch('personal_tui.metrics.Path.read_text', return_value='MemTotal: 1000 kB\nMemAvailable: 400 kB\nMemFree: 100 kB\n'):
            self.assertEqual(memory(), (600 * 1024, 1000 * 1024))

    def test_multiple_nvidia_gpus(self):
        result = subprocess.CompletedProcess([], 0, 'RTX A, 25, 100, 1000\nRTX B, 80, 200, 2000\n')
        with patch('personal_tui.metrics.shutil.which', return_value='/bin/nvidia-smi'), patch('personal_tui.metrics.subprocess.run', return_value=result):
            lines = gpu_lines()
        self.assertEqual(len(lines), 2)
        self.assertIn('25.0%', lines[0])
        self.assertIn('200/2000 MiB', lines[1])

    def test_gpu_timeout_is_unavailable(self):
        with patch('personal_tui.metrics.shutil.which', return_value='/bin/nvidia-smi'), patch('personal_tui.metrics.subprocess.run', side_effect=subprocess.TimeoutExpired('nvidia-smi', 2)):
            self.assertIn('unavailable', gpu_lines()[0])

    def test_missing_linux_metrics_do_not_crash(self):
        with patch('personal_tui.metrics.Path.read_text', side_effect=FileNotFoundError), patch('personal_tui.metrics.gpu_lines', return_value=['GPU: unavailable']):
            lines = Monitor().sample()
        self.assertTrue(all('unavailable' in line for line in lines[1:]))
