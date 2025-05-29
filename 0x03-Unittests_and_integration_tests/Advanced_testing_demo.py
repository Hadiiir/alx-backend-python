"""Advanced testing patterns demonstration"""

import unittest
from unittest.mock import patch, Mock, MagicMock, call
from parameterized import parameterized
import json


class AdvancedTestingDemo(unittest.TestCase):
    """Demonstration of advanced testing patterns"""
    
    def test_parameterized_with_complex_data(self):
        """Example of parameterized testing with complex data structures"""
        test_cases = [
            {
                "name": "simple_nested",
                "input": {"a": {"b": {"c": 1}}},
                "path": ["a", "b", "c"],
                "expected": 1
            },
            {
                "name": "list_access",
                "input": {"items": [{"id": 1}, {"id": 2}]},
                "path": ["items", 0, "id"],
                "expected": 1
            }
        ]
        
        def access_complex_nested(data, path):
            """Helper function to access complex nested structures"""
            result = data
            for key in path:
                if isinstance(result, list):
                    result = result[key]
                else:
                    result = result[key]
            return result
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = access_complex_nested(case["input"], case["path"])
                self.assertEqual(result, case["expected"])
    
    @patch('builtins.open')
    @patch('json.load')
    def test_file_operations_with_mocks(self, mock_json_load, mock_open):
        """Test file operations with comprehensive mocking"""
        # Setup mocks
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_json_load.return_value = {"test": "data"}
        
        def load_config(filename):
            """Function to test"""
            with open(filename, 'r') as f:
                return json.load(f)
        
        # Test the function
        result = load_config("config.json")
        
        # Assertions
        mock_open.assert_called_once_with("config.json", 'r')
        mock_json_load.assert_called_once_with(mock_file)
        self.assertEqual(result, {"test": "data"})
    
    def test_multiple_calls_tracking(self):
        """Test tracking multiple calls to mocked functions"""
        mock_func = Mock()
        mock_func.side_effect = [1, 2, 3, 4]
        
        def process_items(items, processor):
            """Function that calls processor multiple times"""
            return [processor(item) for item in items]
        
        # Test
        result = process_items(['a', 'b', 'c', 'd'], mock_func)
        
        # Verify calls
        expected_calls = [call('a'), call('b'), call('c'), call('d')]
        mock_func.assert_has_calls(expected_calls)
        self.assertEqual(result, [1, 2, 3, 4])
        self.assertEqual(mock_func.call_count, 4)
    
    @parameterized.expand([
        ("valid_email@example.com", True),
        ("invalid-email", False),
        ("", False),
        ("test@", False),
        ("@example.com", False),
    ])
    def test_email_validation(self, email, expected):
        """Parameterized test for email validation"""
        import re
        
        def is_valid_email(email):
            """Simple email validation"""
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        
        result = is_valid_email(email)
        self.assertEqual(result, expected)
    
    def test_context_manager_behavior(self):
        """Test context manager behavior with mocks"""
        mock_resource = Mock()
        
        class TestResource:
            def __init__(self, resource):
                self.resource = resource
            
            def __enter__(self):
                self.resource.connect()
                return self.resource
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.resource.disconnect()
                return False
        
        # Test normal execution
        with TestResource(mock_resource) as resource:
            resource.do_something()
        
        # Verify calls
        mock_resource.connect.assert_called_once()
        mock_resource.do_something.assert_called_once()
        mock_resource.disconnect.assert_called_once()
    
    def test_exception_handling_in_mocks(self):
        """Test exception handling with mocks"""
        mock_service = Mock()
        mock_service.risky_operation.side_effect = ValueError("Something went wrong")
        
        def safe_operation(service):
            """Function that handles exceptions"""
            try:
                return service.risky_operation()
            except ValueError as e:
                return f"Error handled: {e}"
        
        result = safe_operation(mock_service)
        self.assertEqual(result, "Error handled: Something went wrong")
        mock_service.risky_operation.assert_called_once()


# Performance testing example
class TestPerformancePatterns(unittest.TestCase):
    """Examples of performance-related testing patterns"""
    
    def test_caching_behavior(self):
        """Test that caching works correctly"""
        call_count = 0
        
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Simple cache implementation
        cache = {}
        
        def cached_operation(x):
            if x not in cache:
                cache[x] = expensive_operation(x)
            return cache[x]
        
        # Test caching
        result1 = cached_operation(5)
        result2 = cached_operation(5)  # Should use cache
        result3 = cached_operation(10)  # Should call function
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 10)
        self.assertEqual(result3, 20)
        self.assertEqual(call_count, 2)  # Only called twice
    
    def test_batch_processing(self):
        """Test batch processing functionality"""
        def process_batch(items, batch_size=3):
            """Process items in batches"""
            batches = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batches.append([item * 2 for item in batch])
            return batches
        
        items = list(range(10))
        result = process_batch(items, batch_size=3)
        
        expected = [
            [0, 2, 4],      # First batch: 0, 1, 2
            [6, 8, 10],     # Second batch: 3, 4, 5
            [12, 14, 16],   # Third batch: 6, 7, 8
            [18]            # Last batch: 9
        ]
        
        self.assertEqual(result, expected)


# Run all demonstrations
if __name__ == "__main__":
    print("Running Advanced Testing Demonstrations...")
    
    # Run AdvancedTestingDemo
    suite1 = unittest.TestLoader().loadTestsFromTestCase(AdvancedTestingDemo)
    runner1 = unittest.TextTestRunner(verbosity=2)
    result1 = runner1.run(suite1)
    
    print("\nRunning Performance Testing Patterns...")
    
    # Run TestPerformancePatterns
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestPerformancePatterns)
    runner2 = unittest.TextTestRunner(verbosity=2)
    result2 = runner2.run(suite2)
    
    # Final summary
    total_tests = result1.testsRun + result2.testsRun
    total_failures = len(result1.failures) + len(result2.failures)
    total_errors = len(result1.errors) + len(result2.errors)
    
    print(f"\n{'='*60}")
    print(f"ADVANCED TESTING DEMO SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests run: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success rate: {total_tests - total_failures - total_errors}/{total_tests}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 All tests passed! Great job with parameterized testing!")
    else:
        print("❌ Some tests failed. Review the output above for details.")