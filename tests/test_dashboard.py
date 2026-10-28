import io
import json
import re
import unittest
from unittest.mock import patch

from personal_tui.app import render
from personal_tui.metrics import Monitor
from personal_tui.weather import Weather
from personal_tui.layout import dashboard


class DashboardFeatureTests(unittest.TestCase):
    def test_nord_color_preserves_layout_and_respects_no_color(self):
        sections = [('SYSTEM', ['CPU: █████░░░░░ 75.0%'])]
        colored = dashboard(sections, width=100, color=True)
        plain = re.sub(r'\x1b\[[0-9;]*m', '', colored)
        self.assertIn('\x1b[48;2;46;52;64m', colored)
        self.assertIn('\x1b[38;2;235;203;139m75.0%', colored)
        self.assertTrue(all(len(line) == 100 for line in plain.splitlines()))
        with patch('personal_tui.layout.sys.stdout.isatty', return_value=True), patch.dict('os.environ', {'NO_COLOR': '1'}):
            self.assertNotIn('\x1b', dashboard(sections, width=24))

    def test_weather_response_and_cache(self):
        payload = {'current_condition': [{'temp_C': '29', 'FeelsLikeC': '33', 'weatherDesc': [{'value': 'Partly cloudy'}]}]}
        with patch('personal_tui.weather.urlopen') as request:
            request.return_value.__enter__.return_value = io.StringIO(json.dumps(payload))
            weather = Weather('Kuala Lumpur')
            first = weather.sample()
            self.assertIn('29 °C', first[1])
            self.assertEqual(first, weather.sample())
            self.assertEqual(request.call_count, 1)
            self.assertIn('Kuala%20Lumpur', request.call_args.args[0])

    def test_weather_failure_and_unconfigured_location(self):
        with patch('personal_tui.weather.urlopen', side_effect=OSError):
            self.assertIn('unavailable', Weather('City').sample()[1])
        with patch('personal_tui.weather.urlopen') as request:
            Weather('').sample()
            request.assert_not_called()

    def test_storage_and_missing_path(self):
        with patch('personal_tui.metrics.shutil.disk_usage', return_value=(10 * 2**30, 4 * 2**30, 6 * 2**30)):
            lines = Monitor('/').storage()
            self.assertIn('40.0%', lines[1])
            self.assertIn('6.00 GiB free', lines)
        with patch('personal_tui.metrics.shutil.disk_usage', side_effect=OSError):
            self.assertIn('unavailable', Monitor('/missing').storage()[1])

    def test_layout_wraps_without_losing_long_content(self):
        for width in (40, 100):
            output = render({'tasks': [{'text': 'A long task ' * 20, 'done': False}], 'notes': []}, width=width)
            self.assertTrue(all(len(line) <= width for line in output.splitlines()))
            for label in ('SYSTEM', 'WEATHER', 'STORAGE', 'TASKS', 'NOTES'):
                self.assertIn(label, output)
