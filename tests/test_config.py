"""Test configuration management module."""
import os
import importlib

import pytest


def test_conf_import_existing():
    """Test accessing from constant when set."""
    url = 'postgresql://abc@localhost/sample'
    os.environ['MONGODB_URL'] = url
    from payler import config
    assert config.get('MONGODB_URL') == url
    del os.environ['MONGODB_URL']


def test_conf_import_missing():
    """Test error when accessing from missing value."""
    with pytest.raises(RuntimeError):
        from payler import config
        importlib.reload(config)
        config.get('MONGODB_URL')
