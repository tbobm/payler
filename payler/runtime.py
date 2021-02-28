"""Configuration-based runtime execution.

.. code-block:: yaml

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
from typing import Callable, Dict, List, Optional

from payler.errors import ProcessingError


@dataclass
class Workflow:
    """Defines a worfkflow entity, with its logger, action, :class:`AbstractEventLoop`.

    :param name: The workflow name
    :param action: The :class:`Callable` that defines the coroutine
    :param loop: The :class:`AbstractEventLoop` to use in the coroutine
    :param kwargs: Extra arguments
    """
    name: str
    action: Callable[[AbstractEventLoop], None]
    loop: AbstractEventLoop
    future: asyncio.Future = field(init=False)
    kwargs: dict = None

    def register_action(self):
        """Register self.action as an asyncio.Future."""
        self.future = asyncio.ensure_future(self.action(self.loop))


def get_callable(location: str = "payler", process: Optional[str] = None):
    """Find the action to execute using :mod:`asyncio`.

    :param location: defaults to `"payler"` but you can provide custom
        plugins implementing the :class:`payler.driver.BaseDriver`.
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


def register_workflows(workflow_config: List[Dict[str, str]],
                       loop: AbstractEventLoop) -> List[Workflow]:
    """Transform the `workflows` config entry in a list of :class:`Workflow`.

    This function takes the `.workflows` list and creates the corresponding
    :class:`Workflow` which can then be used to start background processes.

    Example input:

    .. code-block:: yaml

        ---
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
