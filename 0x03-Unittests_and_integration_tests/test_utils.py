"""Comprehensive unit tests for utils module"""

import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test cases for access_nested_map function"""
    
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns expected results"""
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)
    
    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test that access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test cases for get_json function"""
    
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test that get_json returns expected payload"""
        # Configure mock
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response
        
        # Call function
        result = get_json(test_url)
        
        # Assertions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test cases for memoize decorator"""
    
    def test_memoize(self):
        """Test that memoize decorator caches function calls"""
        
        class TestClass:
            def a_method(self):
                return 42
            
            @memoize
            def a_property(self):
                return self.a_method()
        
        # Create instance and patch a_method
        test_instance = TestClass()
        
        with patch.object(test_instance, 'a_method', return_value=42) as mock_method:
            # Call a_property twice
            result1 = test_instance.a_property()
            result2 = test_instance.a_property()
            
            # Assertions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()


# Run the tests
if __name__ == "__main__":
    print("Running TestAccessNestedMap...")
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestAccessNestedMap)
    runner1 = unittest.TextTestRunner(verbosity=2)
    result1 = runner1.run(suite1)
    
    print("\nRunning TestGetJson...")
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestGetJson)
    runner2 = unittest.TextTestRunner(verbosity=2)
    result2 = runner2.run(suite2)
    
    print("\nRunning TestMemoize...")
    suite3 = unittest.TestLoader().loadTestsFromTestCase(TestMemoize)
    runner3 = unittest.TextTestRunner(verbosity=2)
    result3 = runner3.run(suite3)
    
    # Summary
    total_tests = result1.testsRun + result2.testsRun + result3.testsRun
    total_failures = len(result1.failures) + len(result2.failures) + len(result3.failures)
    total_errors = len(result1.errors) + len(result2.errors) + len(result3.errors)
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {total_tests} tests run")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success: {total_tests - total_failures - total_errors}/{total_tests}")