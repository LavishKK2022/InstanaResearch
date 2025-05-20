import pytest
from unittest.mock import MagicMock, patch
from aioptim.services.processor import GithubProcessor
import base64
from github import Github, Auth


@pytest.fixture
def processor():
    with patch.object(GithubProcessor, "__post_init__", return_value=None):
        processor = GithubProcessor(
            "accessToken",
            "example_repository",
            "branch"
        )

        file_list = []
        dir = MagicMock()
        dir.type = "dir"
        dir.path = "testPath/"
        for i in range(10):
            file = MagicMock()
            file.content = base64.b64encode("pass".encode())
            file.type = "file"
            if i % 2 == 0:
                file.path = "script.py"
            else:
                file.path = "scode.java"
            file.sha = i
            file_list.append(file)
        file_list.append(dir)
        repository = MagicMock()
        source_branch = MagicMock()
        source_branch.commit.sha = 1
        repository.get_contents.return_value = file_list
        repository.get_branch.return_value = source_branch
        repository.update_file = MagicMock()
        repository.create_git_ref.return_value = True
        repository.update_file = MagicMock()
        processor.github = MagicMock()
        processor.github.get_repo.return_value = repository
        processor.repository_path = "TEST"

        return processor

@pytest.fixture
def method_node():
    code = """
        def test(x):
            return x + 1
    """
    node = MagicMock()
    parent = MagicMock()
    node.parent = parent
    parent.raw_code = code
    node.method = code
    parent.base.path = "script.py"
    return node


@pytest.fixture
def repos():
    repos = []
    repo_names = ["Test/Site", "Test/Accounts", "Test/TestRepostory"]
    for i in range(len(repo_names)):
        repo = MagicMock()
        repo.permissions.pull = True
        repo.permissions.push = True
        repo.name = repo_names[i].split("/")[1]
        repo.full_name = repo_names[i]
        repos.append(repo)
    return repos


def test_creation(repos):
    test_file = "Test/TestRepostory"
    user_repo = "TstRepo"
    mock = MagicMock()
    user_mock = MagicMock()
    user_mock.get_repos.return_value = repos
    mock.get_user.return_value = user_mock
    with patch("aioptim.services.processor.Github", return_value=mock):
        processor = GithubProcessor("test", user_repo, "main")
        assert processor.repository_path == test_file


def test_creation_fails():
    mock = MagicMock()
    user_mock = MagicMock()
    user_mock.get_repos.return_value = []
    mock.get_user.return_value = user_mock
    with patch("aioptim.services.processor.Github", return_value=mock):
        with pytest.raises(FileNotFoundError):
            GithubProcessor("test", "user_repo", "main")


def test_get_item_py(processor):
    assert len(processor['py']) == 5


def test_get_item_java(processor):
    assert len(processor['java']) == 5


def test_get_item_not_exist(processor):
    assert len(processor['test']) == 0
    assert len(processor['']) == 0


def test_update_file_no_code(processor, method_node):
    code = """
        def test(x):
            return x + 2
    """
    mock = processor.github.get_repo()
    contents = MagicMock()
    contents.path = method_node.parent.base.path
    mock.get_contents.return_value = contents
    processor.update_file(method_node, code)
    assert mock.update_file.call_args[1]['path'] == method_node.parent.base.path
    assert mock.update_file.call_args[1]['content'] == method_node.method.replace(
        method_node.method, code)


def test_update_file_with_code(processor):
    assert processor.update_file(None, "") is None
