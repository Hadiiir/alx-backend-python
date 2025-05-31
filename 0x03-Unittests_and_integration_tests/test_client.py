"""
Unit tests for GitHub client
"""

import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient"""
    
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value"""
        # Setup mock
        expected_payload = {"repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        mock_get_json.return_value = expected_payload
        
        # Create client and call org
        client = GithubOrgClient(org_name)
        result = client.org
        
        # Assertions
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, expected_payload)
    
    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        expected_url = "https://api.github.com/orgs/test/repos"
        payload = {"repos_url": expected_url}
        
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("test")
            result = client._public_repos_url
            self.assertEqual(result, expected_url)
    
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        # Setup test data
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = test_payload
        
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/test/repos"
            
            client = GithubOrgClient("test")
            result = client.public_repos()
            
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            
            # Verify mocks were called
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# Integration test fixtures (simplified)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        cls.get_patcher = patch('client.get_json')
        cls.mock_get_json = cls.get_patcher.start()
        
        # Setup side effects for different URLs
        def side_effect(url):
            if "orgs/google" in url and not url.endswith("/repos"):
                return {"repos_url": "https://api.github.com/orgs/google/repos"}
            elif url.endswith("/repos"):
                return [
                    {"name": "repo1", "license": {"key": "apache-2.0"}},
                    {"name": "repo2", "license": {"key": "mit"}},
                    {"name": "repo3", "license": None},
                ]
            return {}
        
        cls.mock_get_json.side_effect = side_effect
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures"""
        cls.get_patcher.stop()
    
    def test_public_repos(self):
        """Integration test for public_repos"""
        client = GithubOrgClient("google")
        repos = client.public_repos()
        expected_repos = ["repo1", "repo2", "repo3"]
        self.assertEqual(repos, expected_repos)
    
    def test_public_repos_with_license(self):
        """Integration test for public_repos with license filter"""
        client = GithubOrgClient("google")
        apache_repos = client.public_repos(license="apache-2.0")
        expected_repos = ["repo1"]
        self.assertEqual(apache_repos, expected_repos)


# Run the tests
if __name__ == '__main__':
    print("Running GitHub Client Tests")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGithubOrgClient))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationGithubOrgClient))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")