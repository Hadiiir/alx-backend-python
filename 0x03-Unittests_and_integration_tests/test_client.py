"""Comprehensive tests for GitHub client"""

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
        result = client.org()
        
        # Assertions
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, expected_payload)
    
    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        with patch.object(GithubOrgClient, 'org', new_callable=PropertyMock) as mock_org:
            # Setup mock payload
            mock_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
            mock_org.return_value = mock_payload
            
            # Create client and test property
            client = GithubOrgClient("google")
            result = client._public_repos_url
            
            # Assertions
            self.assertEqual(result, mock_payload["repos_url"])
    
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        # Setup test data
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = test_payload
        
        with patch.object(GithubOrgClient, '_public_repos_url', new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://api.github.com/orgs/google/repos"
            
            # Create client and call method
            client = GithubOrgClient("google")
            result = client.public_repos()
            
            # Assertions
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            mock_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/google/repos")
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# Mock fixtures for integration tests
class MockFixtures:
    """Mock fixtures for integration testing"""
    
    org_payload = {
        "repos_url": "https://api.github.com/orgs/google/repos",
        "name": "google"
    }
    
    repos_payload = [
        {
            "name": "repo1",
            "license": {"key": "apache-2.0"}
        },
        {
            "name": "repo2", 
            "license": {"key": "mit"}
        },
        {
            "name": "repo3",
            "license": {"key": "apache-2.0"}
        }
    ]
    
    expected_repos = ["repo1", "repo2", "repo3"]
    apache2_repos = ["repo1", "repo3"]


@parameterized_class([
    {
        "org_payload": MockFixtures.org_payload,
        "repos_payload": MockFixtures.repos_payload,
        "expected_repos": MockFixtures.expected_repos,
        "apache2_repos": MockFixtures.apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures and mocks"""
        def side_effect(url):
            """Side effect function for mocking requests.get"""
            mock_response = Mock()
            if "orgs/google" in url and not url.endswith("/repos"):
                mock_response.json.return_value = cls.org_payload
            elif url.endswith("/repos"):
                mock_response.json.return_value = cls.repos_payload
            return mock_response
        
        # Start patcher
        cls.get_patcher = patch('client.get_json')
        cls.mock_get_json = cls.get_patcher.start()
        cls.mock_get_json.side_effect = lambda url: side_effect(url).json()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level mocks"""
        cls.get_patcher.stop()
    
    def test_public_repos(self):
        """Test public_repos method in integration"""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)
    
    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


# Run all tests
if __name__ == "__main__":
    print("Running TestGithubOrgClient...")
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestGithubOrgClient)
    runner1 = unittest.TextTestRunner(verbosity=2)
    result1 = runner1.run(suite1)
    
    print("\nRunning TestIntegrationGithubOrgClient...")
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationGithubOrgClient)
    runner2 = unittest.TextTestRunner(verbosity=2)
    result2 = runner2.run(suite2)
    
    # Summary
    total_tests = result1.testsRun + result2.testsRun
    total_failures = len(result1.failures) + len(result2.failures)
    total_errors = len(result1.errors) + len(result2.errors)
    
    print(f"\n{'='*50}")
    print(f"INTEGRATION TEST SUMMARY: {total_tests} tests run")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success: {total_tests - total_failures - total_errors}/{total_tests}")