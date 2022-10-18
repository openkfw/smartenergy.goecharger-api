import unittest
import sys
sys.path.append('../src')

from src.goecharger.validations import validate_empty_string

class Test(unittest.TestCase):
    def test_validation_ok(self) -> None:
        self.assertEqual(validate_empty_string("test", "hello"), None)

    def test_validation_error(self) -> None:
        self.assertRaises(AssertionError, validate_empty_string, "", "hello")

if __name__ == "__main__":
    unittest.main()