#!/usr/bin/env python3
"""Unittests and integration tests for client.py"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient

TEST_PAYLOAD = [
    (
        {"repos_url": "https://api.github.com/orgs/google/repos"},
        [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}}
        ],
        ["repo1", "repo2"],
        ["repo1"]
    )
]

class TestGithubOrgClient(unittest.TestCase):
    """Class Testing Github Org Client"""

    @parameterized.expand([
        ('google',),
        ('abc',)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        test_class = GithubOrgClient(org_name)
        test_class.org  # Access the property
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test _public_repos_url property"""
        with patch('client.GithubOrgClient.org',
                 new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "https://example.com/repos"}
            test_class = GithubOrgClient('test')
            self.assertEqual(
                test_class._public_repos_url,
                "https://example.com/repos"
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        test_payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                 new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://example.com/repos"
            test_class = GithubOrgClient('test')
            result = test_class.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": TEST_PAYLOAD[0][0],
        "repos_payload": TEST_PAYLOAD[0][1],
        "expected_repos": TEST_PAYLOAD[0][2],
        "apache2_repos": TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class"""

    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect for mock requests"""
            if url == "https://api.github.com/orgs/google":
                return Mock(json=lambda: cls.org_payload)
            if url == "https://api.github.com/orgs/google/repos":
                return Mock(json=lambda: cls.repos_payload)
            return None

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down test class"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos integration"""
        test_class = GithubOrgClient("google")
        self.assertEqual(test_class.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license"""
        test_class = GithubOrgClient("google")
        self.assertEqual(
            test_class.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()