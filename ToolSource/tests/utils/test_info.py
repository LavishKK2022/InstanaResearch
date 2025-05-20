from aioptim.utils.info import get_col, get_row, details
from aioptim.services.parser import PythonParser, JavaParser
import pytest


def test_col_exists():
    col = get_col("language")
    assert col
    assert ["Python", "Java"] == col

    col = get_col("extension")
    assert col
    assert ["py", "java"] == col

    col = get_col("technology")
    assert col
    assert ["pythonRuntimePlatform", "springbootApplicationContainer"] == col

    col = get_col("parser")
    assert col
    assert isinstance(col[0], PythonParser)
    assert isinstance(col[1], JavaParser)


def test_col_not_exists():
    with pytest.raises(LookupError):
        assert get_col("fail")


def test_row_exists():
    row = get_row("Python")
    assert row
    assert 'py' in row
    assert 'pythonRuntimePlatform' in row
    assert isinstance(row[3], PythonParser)

    row = get_row("Java")
    assert row
    assert 'java' in row
    assert 'springbootApplicationContainer' in row
    assert isinstance(row[3], JavaParser)


def test_row_not_exists():
    with pytest.raises(LookupError):
        assert get_row("fail")


def test_details_exists():
    assert details("language", "py") == "Python"
    assert details("py", "language") == "Python"


def test_details_not_exists():
    with pytest.raises(LookupError):
        details("language", "language")
    with pytest.raises(LookupError):
        details("test", "test")
    with pytest.raises(LookupError):
        details("Python", "Java")
