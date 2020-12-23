"""Configuration-based runtime execution.

.. code-block::yaml

    ---
    workflows:
      - name: 'Consume broker payloads and store'
        callable: "client.process_queue"
      - name: "Poll storage and re-inject in RabbitMQ"
        callable: "client.watch_storage"

The default runtime will start every workflow in a background thread.
"""
from asyncio.events import AbstractEventLoop
import asyncio
from dataclasses import dataclass, field
import importlib
from typing import Callable, Dict, List

from payler.errors import ProcessingError


@dataclass
class Workflow:
    """Atomic unit for a thread and its asyncio event_loop."""
    name: str
    action: Callable[[AbstractEventLoop], None]
    loop: AbstractEventLoop
    future: asyncio.Future = field(init=False)

    def register_action(self):
        """Register self.action as an asyncio.Future."""
        self.future = asyncio.ensure_future(self.action(self.loop))


def get_callable(location: str = "payler", process: str = None):
    """Find the action to execute using asyncio.

    `location` defaults to "payler", but anyone can provide custom
    """
    try:
        module = importlib.import_module(location)
        if process is None:
            return module
        target = module
        for attr in process.split('.'):
            target = getattr(target, attr)
        return target
    except ModuleNotFoundError as err:
        raise ProcessingError(
            f'Could not find module {location}'
        ) from err
    except AttributeError as err:
        raise ProcessingError(
            'Could not find process {process} in {location}'
        ) from err


def register_workflows(workflow_config: List[Dict[str, str]], loop: AbstractEventLoop) -> List[Workflow]:
    """Transform the `workflows` config entry in a list of `Workflow`.

    This function takes the `.workflows` list and creates the corresponding
    Workflow, which can then be used to start background processes.

    Example input:

    .. code-bloc::yaml

        - name: "Consume broker payloads and store in MongoDB"
          callable: "client.process_queue"
        - name: "Poll storage and re-inject in RabbitMQ"
          callable: "client.watch_storage"
    """
    workflows = []
    for item in workflow_config:
        workflow = Workflow(
            item.get('name', 'unnamed'),
            get_callable(process=item.get('callable')),
            loop,
        )
        workflows.append(workflow)
    return workflows
