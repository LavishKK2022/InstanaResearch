import pytest
from aioptim.services.AIclassifier import AIClassifier
from aioptim.services.generator import Generator
from unittest.mock import MagicMock, patch


@pytest.fixture
def classifier():
    return AIClassifier("tinyllama:latest", "http://test.com", 3)


def find_match(list, target):
    for member in list:
        if member == target:
            return True
    return False


@pytest.fixture
def short_snippet():
    code_node = MagicMock()
    code_node.method = """
    def find_match(list, target):
        for member in list:
            if member == target:
                return True
        return False
    """
    return code_node


@pytest.fixture
def long_snippet():
    code_node = MagicMock()
    code_node.method = """
    def parse_file_methods(self, file):
        def process_match(matches):
            for match in matches:
                matched_items = match[1]
                method_signature = matched_items['identifier'][0].text.decode()
                parameters = matched_items['parameters'][0].text.decode()
                decorator = matched_items.get('decorator', None)
                if decorator:
                    decorator = decorator[0].text.decode()
                method = matched_items['method'][0].text.decode()
                file.methods[
                    method_signature
                ] = Node.FileNode.MethodNode(
                    parent=file,
                    id=matched_items['identifier'][0].text.decode(),
                    params=parameters,
                    method=method,
                    decorator=decorator
                )

        tree = self.parser.parse(file.raw_code.encode())
        process_match(self.queries['method_query'].matches(tree.root_node))
        process_match(self.queries['decorator_query'].matches(tree.root_node))
    """
    return code_node


def test_classify_slow_short_code_snippet(classifier, short_snippet):
    with patch.object(Generator, "_send", return_value='slow') as mock:
        with patch.object(Generator, "_replace", return_value="PROMPTXYZ <code> PROMPTXYZ"):
            result = classifier(short_snippet)
            assert result[0].method == short_snippet.method
            mock.assert_called_once_with("PROMPTXYZ <code> PROMPTXYZ")


def test_classify_fast_short_code_snippet(classifier, short_snippet):
    with patch.object(Generator, "_send", return_value='fast') as mock:
        with patch.object(Generator, "_replace", return_value="PROMPTXYZ <code> PROMPTXYZ"):
            result = classifier(short_snippet)
            assert len(result) == 0
            mock.assert_called_once_with("PROMPTXYZ <code> PROMPTXYZ")


def test_classify_slow_long_code_snippet(classifier, long_snippet):
    with patch.object(Generator, "_send", return_value='slow') as mock:
        with patch.object(Generator, "_replace", return_value="PROMPTXYZ <code> PROMPTXYZ"):
            result = classifier(long_snippet)
            assert result[0].method == long_snippet.method
            mock.assert_called_once_with("PROMPTXYZ <code> PROMPTXYZ")


def test_classify_fast_long_code_snippet(classifier, long_snippet):
    with patch.object(Generator, "_send", return_value='fast') as mock:
        with patch.object(Generator, "_replace", return_value="PROMPTXYZ <code> PROMPTXYZ"):
            result = classifier(long_snippet)
            assert len(result) == 0
            mock.assert_called_once_with("PROMPTXYZ <code> PROMPTXYZ")
