#!/usr/bin/env python3
"""Test module for client.GithubOrgClient"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    # Task 4: Parameterize and patch as decorators
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value
        
        Args:
            org_name: Name of the organization to test
            mock_get_json: Mock of get_json function
        """
        test_client = GithubOrgClient(org_name)
        test_client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    # Task 5: Mocking a property
    def test_public_repos_url(self):
        """Test _public_repos_url property returns expected value"""
        with patch('client.GithubOrgClient.org',
                  new_callable=PropertyMock) as mock_org:
            test_payload = {"repos_url": "https://example.com/repos"}
            mock_org.return_value = test_payload
            test_client = GithubOrgClient("test")
            result = test_client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

    # Task 6: More patching
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected list of repos"""
        test_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://example.com/repos"
            test_client = GithubOrgClient("test")
            result = test_client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()

    # Task 7: Parameterize
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license returns expected boolean
        
        Args:
            repo: Repository dictionary
            license_key: License key to check
            expected: Expected return value
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# Tasks 8 & 9: Integration tests
@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class with mock for requests.get"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect to return different payloads based on URL"""
            if url == "https://api.github.com/orgs/google":
                return Mock(json=lambda: cls.org_payload)
            if url == "https://api.github.com/orgs/google/repos":
                return Mock(json=lambda: cls.repos_payload)
            return None

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos from fixtures"""
        test_client = GithubOrgClient("google")
        self.assertEqual(test_client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        test_client = GithubOrgClient("google")
        self.assertEqual(
            test_client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()