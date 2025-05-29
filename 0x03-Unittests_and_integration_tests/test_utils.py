#!/usr/bin/env python3
"""
Test for utils module
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from typing import Mapping, Sequence, Any, Dict


class TestAccessNestedMap(unittest.TestCase):
    """Tests for access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map: Mapping,
                              path: Sequence, expected: Any) -> None:
        """Test access_nested_map with valid inputs"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b"))
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping,
                                        path: Sequence) -> None:
        """Test access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map, path)


class TestGetJson(unittest.TestCase):
    """Tests for get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url: str, test_payload: Dict) -> None:
        """Test get_json returns expected result"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(json=Mock(return_value=test_payload))
            self.assertEqual(get_json(test_url), test_payload)
            mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Tests for memoize decorator"""

    def test_memoize(self) -> None:
        """Test memoize caches the result"""
        class TestClass:
            """Test class for memoization"""
            def a_method(self) -> int:
                return 42

            @memoize
            def a_property(self) -> int:
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_method:
            mock_method.return_value = 42
            test = TestClass()
            self.assertEqual(test.a_property(), 42)
            self.assertEqual(test.a_property(), 42)
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()