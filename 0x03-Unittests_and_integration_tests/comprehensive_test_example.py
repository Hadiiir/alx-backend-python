"""
Comprehensive example demonstrating all testing patterns
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from parameterized import parameterized


class ComprehensiveTestExample(unittest.TestCase):
    """Demonstrates various testing patterns and best practices"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_data = {
            "simple": {"a": 1, "b": 2},
            "nested": {"a": {"b": {"c": 3}}},
            "list": {"items": [1, 2, 3, 4, 5]}
        }
    
    def tearDown(self):
        """Clean up after each test method"""
        pass
    
    @parameterized.expand([
        # Test case format: (test_name, input_data, expected_output)
        ("simple_access", {"a": 1}, ("a",), 1),
        ("nested_access", {"a": {"b": 2}}, ("a", "b"), 2),
        ("deep_nested", {"x": {"y": {"z": "value"}}}, ("x", "y", "z"), "value"),
    ])
    def test_parameterized_access(self, name, nested_map, path, expected):
        """Example of parameterized testing with descriptive names"""
        from utils import access_nested_map
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected, f"Failed for test case: {name}")
    
    @parameterized.expand([
        # Error test cases
        ("empty_dict", {}, ("a",)),
        ("missing_key", {"a": 1}, ("b",)),
        ("deep_missing", {"a": {"b": 1}}, ("a", "c")),
    ])
    def test_parameterized_exceptions(self, name, nested_map, path):
        """Example of parameterized exception testing"""
        from utils import access_nested_map
        with self.assertRaises(KeyError, msg=f"Should raise KeyError for: {name}"):
            access_nested_map(nested_map, path)
    
    @patch('builtins.print')  # Mock print to capture output
    def test_with_mock_patch_decorator(self, mock_print):
        """Example using patch as decorator"""
        def sample_function():
            print("Hello, World!")
            return "done"
        
        result = sample_function()
        
        # Verify the function was called and print was mocked
        mock_print.assert_called_once_with("Hello, World!")
        self.assertEqual(result, "done")
    
    def test_with_mock_context_manager(self):
        """Example using patch as context manager"""
        with patch('builtins.len') as mock_len:
            mock_len.return_value = 42
            
            # Test that our mock is working
            result = len([1, 2, 3])  # Would normally return 3
            self.assertEqual(result, 42)
            mock_len.assert_called_once_with([1, 2, 3])
    
    def test_mock_side_effects(self):
        """Example of using side_effect for dynamic mock behavior"""
        with patch('builtins.len') as mock_len:
            # side_effect can be a function
            mock_len.side_effect = lambda x: len(str(x))
            
            result1 = len([1, 2, 3])  # len(str([1, 2, 3]))
            result2 = len("hello")    # len(str("hello"))
            
            self.assertEqual(result1, 9)  # "[1, 2, 3]" has 9 characters
            self.assertEqual(result2, 5)  # "hello" has 5 characters
    
    def test_mock_multiple_calls(self):
        """Example of testing multiple calls to the same mock"""
        with patch('builtins.max') as mock_max:
            mock_max.side_effect = [10, 20, 30]  # Return different values
            
            result1 = max([1, 2, 3])
            result2 = max([4, 5, 6])
            result3 = max([7, 8, 9])
            
            self.assertEqual(result1, 10)
            self.assertEqual(result2, 20)
            self.assertEqual(result3, 30)
            self.assertEqual(mock_max.call_count, 3)
    
    def test_property_mocking(self):
        """Example of mocking properties"""
        class SampleClass:
            @property
            def expensive_property(self):
                # Simulate expensive operation
                return sum(range(1000000))
        
        obj = SampleClass()
        
        with patch.object(SampleClass, 'expensive_property', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = 42
            
            result = obj.expensive_property
            self.assertEqual(result, 42)
            mock_prop.assert_called_once()
    
    def test_assert_methods_comprehensive(self):
        """Comprehensive example of various assert methods"""
        # Basic equality
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual(1 + 1, 3)
        
        # Truth testing
        self.assertTrue(bool([1, 2, 3]))
        self.assertFalse(bool([]))
        
        # Membership testing
        self.assertIn('a', 'abc')
        self.assertNotIn('d', 'abc')
        
        # Type testing
        self.assertIsInstance([], list)
        self.assertIsNone(None)
        self.assertIsNotNone([])
        
        # Numeric comparisons
        self.assertGreater(5, 3)
        self.assertLess(3, 5)
        self.assertGreaterEqual(5, 5)
        self.assertLessEqual(3, 5)
        
        # String testing
        self.assertRegex('hello123', r'hello\d+')
        self.assertCountEqual([1, 2, 3], [3, 2, 1])  # Same elements, any order
        
        # Container testing
        self.assertListEqual([1, 2, 3], [1, 2, 3])
        self.assertDictEqual({'a': 1}, {'a': 1})
    
    def test_custom_assertions(self):
        """Example of creating custom assertion logic"""
        def assert_all_positive(numbers):
            """Custom assertion to check all numbers are positive"""
            for num in numbers:
                if num <= 0:
                    self.fail(f"Found non-positive number: {num}")
        
        # This should pass
        assert_all_positive([1, 2, 3, 4, 5])
        
        # This would fail (commented out to avoid test failure)
        # assert_all_positive([1, 2, -3, 4, 5])


# Demonstration of test discovery and execution
def run_comprehensive_tests():
    """Run all tests and provide detailed output"""
    print("Running Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ComprehensiveTestExample)
    
    # Run tests with maximum verbosity
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(suite)
    
    # Detailed results
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_tests()
    print(f"\nOverall test suite: {'PASSED' if success else 'FAILED'}")