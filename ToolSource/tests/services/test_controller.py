import pytest
from prefect.testing.utilities import prefect_test_harness
import logging
from unittest.mock import patch, MagicMock, call
from aioptim.services.parser import PythonParser
from aioptim.utils.node import Node
from aioptim.services.controller import (
    schedule_service,
    service,
    endpoints,
    fault_line,
    slow_code,
    generate_code,
    push_code
)


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


@pytest.fixture(scope="session", autouse=True)
def pytest_logging():
    logging.getLogger("prefect").setLevel(logging.CRITICAL)
    yield


@pytest.fixture
def py_raw_code():
    return """
    @app.route("/login")
    def login(user):
        authentateUser()
        if user:
            fetchDetails()
        else:
            signUP()
        return "User is logged in"

    def authenticateUser():
        if self.user_exists:
            return True
        return False

    def signUP():
        return signUpContent()

    @app.route("/get-file")
    def retrieve_file():
        content = findContent()
        return content
    """


@pytest.fixture
def py_file_node(py_raw_code):
    file = MagicMock()
    file.raw_code = py_raw_code
    file.methods = {}
    file.base.path = "src/aioptim/module"
    file.extend = lambda new_methods: file.methods.update(new_methods)
    return file


@pytest.fixture
def state():
    state = MagicMock()
    state.reset_return_value = True
    return state


@pytest.fixture
def special_state():
    state = MagicMock(spec=[])
    state.reset_return_value = True
    return state


def test_schedule_service():
    with patch("aioptim.services.controller.service") as mock:
        schedule_service(100, 100, {"test": "test"}, True, "TEST")
        mock.assert_called_once_with("TEST")


def test_service():
    state = MagicMock()
    state.reset.return_value = True
    with patch("aioptim.services.controller.endpoints") as m_endpoints:
        with patch("aioptim.services.controller.fault_line") as m_fault_line:
            with patch("aioptim.services.controller.slow_code") as m_slow_code:
                with patch("aioptim.services.controller.generate_code") as m_generate_code:
                    with patch("aioptim.services.controller.push_code") as m_push_code:
                        service(state)
                        m_endpoints.assert_called_once()
                        m_fault_line.assert_called_once()
                        m_slow_code.assert_called_once()
                        m_generate_code.assert_called_once()
                        m_push_code.assert_called_once()


def test_endpoints(state):
    node = [
        Node.EndpointNode(
            "label",
            "technology",
            5
        )
    ]
    state.ibm.filter_endpoints.return_value = node
    endpoints(state)
    assert state.endpoints and state.endpoints == node


def test_fault_line(state, py_file_node):
    state.endpoints = [
        Node.EndpointNode(
            "label",
            "pythonRuntimePlatform",
            5
        )
    ]

    state.processor = {"py": [py_file_node]}
    fault_line(state)
    assert state.fault_line


def test_fault_line_no_endpoints(special_state):
    fault_line(special_state)
    assert not hasattr(special_state, "endpoints")


def test_slow_code_one_method(state):
    state.fault_line = [MagicMock()]
    slow_code(state)
    assert state.slow_code_blocks
    assert len(state.slow_code_blocks) == 1


def test_slow_code_multiple_methods(state):
    state.classifier = MagicMock()
    state.classifier.return_value = None
    res1 = MagicMock()
    res2 = MagicMock()
    state.fault_line = [res1, res2]
    slow_code(state)
    state.classifier.assert_called()
    state.classifier.assert_has_calls([call(res1, res2)], any_order=True)


def test_generate_code(state, py_file_node):
    PythonParser().parse_file_methods(py_file_node)
    state.slow_code_blocks = py_file_node.methods.values()
    state.generator.__bool__.return_value = True
    state.generator.max_runs = 1
    state.generator.describe.return_value = "Test description"
    state.generator.generate.return_value = "Test code"
    state.generator.validate.return_value = True
    generate_code(state)
    for block in state.slow_code_blocks:
        assert block.generated_code == "Test code"


def test_generate_code_model_invalid(state, py_file_node):
    PythonParser().parse_file_methods(py_file_node)
    state.slow_code_blocks = py_file_node.methods.values()
    state.generator.model = "test-model"
    state.generator.__bool__.return_value = False
    with pytest.raises(LookupError):
        generate_code(state)


def test_slow_code_no_methods(special_state):
    slow_code(special_state)
    assert not hasattr(special_state, "slow_code_blocks")


def test_generate_code_no_slow_code_blocks(state):
    delattr(state, "slow_code_blocks")
    generate_code(state)
    assert not hasattr(state, "slow_code_blocks")


def test_push_code(state, py_file_node):
    PythonParser().parse_file_methods(py_file_node)
    state.slow_code_blocks = py_file_node.methods.values()
    for slow_code_block in state.slow_code_blocks:
        slow_code_block.generated_code = "TEST"
    state.processor = MagicMock()
    state.processor.update_file.return_value = None
    push_code(state)
    calls = []
    for block in state.slow_code_blocks:
        calls.append(call(block, "TEST"))
    state.processor.update_file.assert_has_calls(calls, any_order=True)


def test_push_code_no_generated_code(special_state):
    special_state.slow_code_blocks = [
        MagicMock(spec=[]) for i in range(10)]
    special_state.processor = MagicMock()
    special_state.processor.update_file.return_value = None
    push_code(special_state)
    special_state.processor.update_file.assert_not_called()
