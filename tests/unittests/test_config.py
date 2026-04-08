import unittest
from unittest.mock import patch

from tap_uservoice.config import validate_config, load_config, get_config_start_date


class TestValidateConfig(unittest.TestCase):
    """Test config validation."""

    def test_valid_config(self):
        """Test that valid config passes validation."""
        config = {'subdomain': 'test', 'api_key': 'key', 'api_secret': 'secret'}
        # Should not raise
        validate_config(config)

    def test_missing_subdomain_raises(self):
        """Test that missing subdomain raises RuntimeError."""
        config = {'api_key': 'key', 'api_secret': 'secret'}
        with self.assertRaises(RuntimeError):
            validate_config(config)

    def test_null_subdomain_raises(self):
        """Test that null subdomain raises RuntimeError."""
        config = {'subdomain': None, 'api_key': 'key'}
        with self.assertRaises(RuntimeError):
            validate_config(config)


class TestGetConfigStartDate(unittest.TestCase):
    """Test get_config_start_date."""

    def test_parse_start_date(self):
        """Test parsing a valid start date."""
        config = {'start_date': '2024-01-01T00:00:00Z'}
        result = get_config_start_date(config)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    def test_parse_start_date_with_timezone(self):
        """Test parsing a start date with timezone."""
        config = {'start_date': '2024-06-15T12:00:00+05:30'}
        result = get_config_start_date(config)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)


class TestLoadConfig(unittest.TestCase):
    """Test load_config."""

    @patch('builtins.open',
           unittest.mock.mock_open(
               read_data='{"subdomain": "test", "api_key": "k", "api_secret": "s"}'))
    def test_load_valid_config(self):
        """Test loading a valid config file."""
        config = load_config('/tmp/config.json')
        self.assertEqual(config['subdomain'], 'test')

    @patch('builtins.open',
           unittest.mock.mock_open(read_data='invalid json'))
    def test_load_invalid_json_raises(self):
        """Test that invalid JSON raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            load_config('/tmp/bad_config.json')


if __name__ == '__main__':
    unittest.main()
