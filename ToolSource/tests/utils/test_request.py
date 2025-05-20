from aioptim.utils.request import Conn
from unittest.mock import patch, MagicMock
import pytest
from requests import RequestException


@pytest.fixture
def conn():
    conn = Conn()
    conn.url = "http://test.com"
    return conn


@pytest.fixture
def response_data():
    return {"test": "test"}


@pytest.fixture
def get(response_data):
    get = MagicMock()
    get.json.return_value = response_data
    return get


@pytest.fixture
def post(response_data):
    post = MagicMock()
    post.json.return_value = response_data
    return post


def test_construct_path_with_nothing(conn):
    assert conn._construct_path() == ""


def test_construct_path_with_valid_parts(conn):
    assert conn._construct_path(
        "www.test.com", "/test", "/api") == 'www.test.com/test/api'


def test_get_req(conn, get, response_data):

    with patch(f"{Conn.__module__}.get", return_value=get):
        assert conn.get_req("/api", "None", "None") == response_data


def test_post_req(conn, post, response_data):
    with patch(f"{Conn.__module__}.post", return_value=post):
        assert conn.post_req("/api", {}, "None", "None") == response_data


def test_get_req_invalid_returned(conn, get):
    with patch(f"{Conn.__module__}.get", side_effect=RequestException()):
        with pytest.raises(ConnectionError):
            conn.get_req("/api", "None", "None")

    get.json.side_effect = Exception()

    with patch(f"{Conn.__module__}.get", return_value=get):
        with pytest.raises(ConnectionError):
            conn.get_req("/api", "None", "None")


def test_post_req_invalid_returned(conn, post):
    with patch(f"{Conn.__module__}.post", side_effect=RequestException()):
        with pytest.raises(ConnectionError):
            conn.post_req("/api", {}, "None", "None")

    post.json.side_effect = Exception()

    with patch(f"{Conn.__module__}.post", return_value=post):
        with pytest.raises(ConnectionError):
            conn.post_req("/api", {}, "None", "None")
