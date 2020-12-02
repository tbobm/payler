"""Import and dump informations."""
from datetime import timedelta
import typing

import yaml

from animator.structs import Answer, Question, Workflow


def import_workflow_from_yaml(data: typing.IO) -> Workflow:
    """Load a YAML and return a Workflow.

    .. code-block:: yaml

       ---
       title: Base Workflow
       questions:
         - title: "What is your Quest ?"
           choices:
             - name: "Become the best Pakemanz Master."
             - name: "Gather intel about Evilman."
         - title: "What is your Name ?"
           choices:
             - name: "Bob"
             - name: "Ash"
             - name: "Patrick"
             - name: "Han Alone"

    """
    content = yaml.safe_load(data)
    workflow = _create_workflow(content)
    return workflow


def _create_answer(choice: typing.Dict[str, str]) -> Answer:
    return Answer(title=choice['name'])


def _create_question(data: typing.Dict) -> Question:
    choices = data['choices']
    answers = [_create_answer(choice) for choice in choices]
    question = Question(
        title=data['title'],
        choices=answers,
    )
    return question


def _create_workflow(content: typing.Any) -> Workflow:
    elements = content.get('questions')
    duration = content.get('duration', None)
    questions = [
        _create_question(element) for element in elements
    ]
    if duration:
        workflow = Workflow(
            title=content.get('title'),
            questions=questions,
            duration=timedelta(seconds=duration),
        )
        return workflow
    workflow = Workflow(
        title=content.get('title'),
        questions=questions,
    )
    return workflow
