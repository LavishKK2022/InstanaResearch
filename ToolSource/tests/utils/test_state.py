from aioptim.utils.state import State
from aioptim.services.instana import IBM
from aioptim.services.classifier import Classifier
from aioptim.services.generator import Generator
from aioptim.services.processor import GithubProcessor
import pytest
from unittest.mock import patch


@pytest.fixture
def ibm():
    return IBM(
        "test", "test", "apiTest", "testLabel", 5
    )


@pytest.fixture
def classifier():
    return Classifier()


@pytest.fixture
def generator():
    return Generator(
        "testModel", "http://test.com", 5
    )


@pytest.fixture
def processor():
    with patch.object(GithubProcessor, "__post_init__", return_value=None):
        return GithubProcessor(
            "tokenTest", "repoTest", "main"
        )


@pytest.fixture
def state(ibm, classifier, generator, processor):
    return State(
        ibm, generator, processor, classifier, 10, 5
    )


def test_state_reset_without_adding(state):
    state_dict = state.__dict__
    state.reset()
    assert state.__dict__ == state_dict


def test_state_reset_with_adding(state):
    state_dict = state.__dict__
    state.test = 5
    state.reset()
    assert state.__dict__ == state_dict
