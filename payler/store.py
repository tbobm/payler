"""Database entities and functions related to content management."""
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from animator import db, structs


Base = declarative_base()


# NOTE: could be moved to a store.entities module?
class Answer(Base):  # pylint: disable=too-few-public-methods
    """Answer entity in the Database."""
    __tablename__ = 'answer'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    score = Column(Integer)
    question_id = Column(Integer, ForeignKey('question.id'))
    question = sa.orm.relationship('Question', back_populates='answers')


class Question(Base):  # pylint: disable=too-few-public-methods
    """Question entity in the Database."""
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    answers = sa.orm.relationship('Answer', back_populates='question')
    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = sa.orm.relationship('Workflow', back_populates='questions')


class Workflow(Base):  # pylint: disable=too-few-public-methods
    """Question entity in the Database."""
    __tablename__ = 'workflow'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    questions = sa.orm.relationship('Question', back_populates='workflow')


def store_workflow(sessionmaker: sa.orm.sessionmaker, workflow: structs.Workflow) -> Workflow:
    """Register a Workflow and its childrens in DB."""
    session = sessionmaker()
