"""Test cases for the validation module"""
import unittest
import sys
from src.goechargerv2.validations import validate_empty_string

sys.path.append("../src")


class Test(unittest.TestCase):
    """Unit tests testing validations."""

    def test_validation_ok(self) -> None:
        """Test if a non empty string is valid, thus returns None"""
        self.assertEqual(validate_empty_string("test", "hello"), None)

    def test_validation_error(self) -> None:
        """Test if an empty string is raises an error"""
        self.assertRaises(AssertionError, validate_empty_string, "", "hello")


if __name__ == "__main__":
    unittest.main()
