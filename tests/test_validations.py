"""Test cases for the validation module"""
import pytest

from src.goechargerv2.validations import validate_empty_string


def test_validation_ok() -> None:
    """Test if a non empty string is valid, thus returns None"""
    assert validate_empty_string("test", "hello") is None


def test_validation_error() -> None:
    """Test if an empty string is raises an error"""
    with pytest.raises(Exception) as exception_info:
        validate_empty_string("", "hello")
    assert str(exception_info.value) == "hello must be specified"
