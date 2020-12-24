"""Test runtime-related operations."""
import asyncio
import importlib
from unittest.mock import MagicMock
import pytest

from payler.errors import ProcessingError
from payler import runtime


@pytest.mark.parametrize('process', [
    ('client.process_queue'),
    ('client.watch_storage'),
])
def test_get_callable(process):
    """Ensure we find the default callables."""
    workflow = runtime.get_callable(process=process)
    assert callable(workflow) is True


def test_get_callable_module(monkeypatch):
    """Ensure we find the default callables."""
    def mockreturn(location):
        """Fake callable module."""
        mock = MagicMock()
        mock.name = location
        return mock

    monkeypatch.setattr(importlib, 'import_module', mockreturn)

    workflow = runtime.get_callable(location='mocked')
    assert callable(workflow) is True


def test_callable_error():
    """Ensure proper handling of unexistent workflow."""
    with pytest.raises(ProcessingError):
        runtime.get_callable('dummy', process='missing')


def test_unknown_callable():
    """Ensure proper handling of unexistent workflow."""
    with pytest.raises(ProcessingError):
        runtime.get_callable(process='client.not_exist')


def test_register_workflows(event_loop):
    """Ensure example configuration is registerable."""
    workflow_config = {
            'name': 'Consumer broker payloads',
            'callable': 'client.process_queue',
        }
    workflow = runtime.register_workflows([workflow_config], event_loop)
    assert workflow[0].name == workflow_config['name']
    assert callable(workflow[0].action)
