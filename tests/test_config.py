"""Test configuration management module."""
import io

import pytest

from payler import config


def test_conf_import_existing(monkeypatch):
    """Test accessing from constant when set."""
    url = 'postgresql://abc@localhost/sample'
    monkeypatch.setenv('MONGODB_URL', url)
    assert config.get('MONGODB_URL') == url


def test_conf_import_default(monkeypatch):
    """Test default when accessing from missing known setting."""
    monkeypatch.delenv('MONGODB_URL', raising=False)
    mongo = config.get('MONGODB_URL')
    assert config.AVAILABLE_SETTINGS['MONGODB_URL'] == mongo


def test_conf_import_unknown(monkeypatch):
    """Test error when accessing unkown setting."""
    monkeypatch.delenv('EXAMPLE', raising=False)
    with pytest.raises(RuntimeError):
        config.get('EXAMPLE')


def test_load_config(example_config):
    """Ensure we can properly load a YAML file."""
    config.load(example_config)
