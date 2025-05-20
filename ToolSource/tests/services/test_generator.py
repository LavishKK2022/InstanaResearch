import pytest
from aioptim.services.generator import Generator
from unittest.mock import MagicMock, patch
from aioptim.utils.config import Prompt
from aioptim.utils.request import Conn


@pytest.fixture
def generator():
    return Generator("tinyllama:latest", "http://test.com", 3)


@pytest.fixture
def other_generator():
    return Generator("none", "http://test.com", 3)


@pytest.fixture
def bool_response():
    return {
        'models':
            [
                {
                    'name': 'tinyllama:latest',
                    'model': 'tinyllama:latest',
                    'modified_at': '2025-04-15T01:19',
                    'size': 637700138,
                    'digest': 'digest',
                    'details': {
                        'parent_model': '',
                        'format': 'gguf',
                        'family': 'llama',
                        'families': ['llama'],
                        'parameter_size': '1B',
                        'quantization_level':
                        'Q4_0'
                    }
                }
            ]
    }


@pytest.fixture
def model_response():
    return {
        "model": "tinyllama:latest",
        "created_at": "2025-04-15T01:31:39",
        "response": "This is a test response",
        "done": True,
        "done_reason": "stop",
        "context": [
            529,
            1286,
            29991,
        ],
        "total_duration": 390165374,
        "load_duration": 5023503,
        "prompt_eval_count": 39,
        "prompt_eval_duration": 2930483,
        "eval_count": 153,
        "eval_duration": 381856658,
    }


@pytest.fixture
def invalid_model_response():
    return {
        "model": "tinyllama:latest",
        "created_at": "2025-04-15T01:31:39",
        "done": True,
        "done_reason": "stop",
        "context": [
            529,
            1286,
            29991,
        ],
        "total_duration": 390165374,
        "load_duration": 5023503,
        "prompt_eval_count": 39,
        "prompt_eval_duration": 2930483,
        "eval_count": 153,
        "eval_duration": 381856658,
    }


def test_generator_creation(generator):
    assert generator.prompts == Prompt.get_contents()


def test_replace_with_valid_key():
    res = Generator._replace("This is a $TEST$ test", {"$TEST$": "successful"})
    assert res == "This is a successful test"


def test_replace_with_invalid_key():
    res = Generator._replace("This is a $TEST$ test", {"$NA$": "successful"})
    assert res == "This is a $TEST$ test"


def test_model_exists_bool(bool_response, generator):
    with patch.object(Conn, "get_req", return_value=bool_response):
        assert generator


def test_model_not_exist_bool(bool_response, other_generator):
    with patch.object(Conn, "get_req", return_value=bool_response):
        assert not other_generator


def test_send_prompt(generator, model_response):
    with patch.object(Conn, "post_req", return_value=model_response):
        res = generator._send("This is a test")
        assert res == "This is a test response"


def test_send_prompt_check_exception(generator, invalid_model_response):
    with patch.object(Conn, "post_req", return_value=invalid_model_response):
        with pytest.raises(ValueError):
            generator._send("This is a test")


def test_generate(generator,  model_response):
    with patch.object(Generator, "_send", return_value=model_response) as mock:
        with patch.object(Generator, "_replace", return_value="Test response"):
            generator.generate("def res(): pass", "res", "Python")
            mock.assert_called_once_with("Test response")


def test_describe(generator, model_response):
    with patch.object(Generator, "_send", return_value=model_response) as mock:
        with patch.object(Generator, "_replace", return_value="Test response"):
            generator.describe("def res(): pass", "Python")
            mock.assert_called_once_with("Test response")


def test_validate_valid(generator):
    with patch.object(Generator, "_send", return_value="yes"):
        with patch.object(Generator, "_replace", return_value="Test response"):
            assert generator.validate(
                "problem description",
                "code",
                "language"
            )


def test_validate_invalid(generator):
    with patch.object(Generator, "_send", return_value="no"):
        with patch.object(Generator, "_replace", return_value="Test response"):
            assert not generator.validate(
                "problem description",
                "code",
                "language"
            )
