from aioptim.utils.node import Node
from unittest.mock import MagicMock
import pytest
import base64


@pytest.fixture
def file_node():
    base_file = MagicMock()
    base_file.path = "test/test.py"
    base_file.content = base64.b64encode("test".encode())
    return Node.FileNode(
        base_file
    )


@pytest.fixture
def method_node(file_node):
    return Node.FileNode.MethodNode(
        file_node,
        "test_function",
        "x",
        "def test_function(x): /n/t return None",
        None
    )


@pytest.fixture
def method_node_polymorphic(file_node):
    return Node.FileNode.MethodNode(
        file_node,
        "test_function",
        "x",
        "def test_function(x): /n/t return 5",
        None
    )


@pytest.fixture
def diff_method_node(file_node):
    return Node.FileNode.MethodNode(
        file_node,
        "different_test_function",
        "y",
        "def different_test_function(y): /n/t return None",
        None
    )


def test_method_node_hash(method_node):
    assert hash((method_node.id, method_node.params)) == hash(method_node)


def test_method_node_eq(method_node, method_node_polymorphic, diff_method_node):
    assert method_node == method_node_polymorphic
    assert method_node != diff_method_node


def test_file_node_extend_with_methods(file_node, method_node, diff_method_node):
    data = {
        method_node.id: method_node,
        diff_method_node.id: diff_method_node
    }
    file_node.extend(data)
    assert len(file_node.methods) == 2


def test_file_node_extend_without_methods(file_node):
    file_node.extend({})
    assert not file_node.methods
