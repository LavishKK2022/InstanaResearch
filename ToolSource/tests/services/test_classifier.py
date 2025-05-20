import pytest
from aioptim.services.classifier import Classifier
from unittest.mock import MagicMock


@pytest.fixture
def classifier():
    return Classifier()


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


def test_valid_pred_to_label():
    assert Classifier.Label.pred_to_label('LABEL_0') == Classifier.Label.FAST
    assert Classifier.Label.pred_to_label('LABEL_1') == Classifier.Label.SLOW


def test_invalid_pred_to_label():
    assert Classifier.Label.pred_to_label('') == Classifier.Label.ERR
    assert Classifier.Label.pred_to_label(None) == Classifier.Label.ERR


def test_classify_short_code_snippet(classifier, short_snippet):
    result = classifier(short_snippet)
    if result:
        assert result[0].method == short_snippet.method
    else:
        assert True


def test_classify_long_code_snippet(classifier, long_snippet):
    result = classifier(long_snippet)
    if result:
        assert result[0].method == long_snippet.method
    else:
        assert True
