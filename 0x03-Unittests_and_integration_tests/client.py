#!/usr/bin/env python3
"""Client module for interacting with the GitHub API"""

import requests
from typing import List, Dict


def get_json(url: str) -> Dict:
    """Returns the JSON content of a given URL"""
    response = requests.get(url)
    return response.json()


class GithubOrgClient:
    """Client for GitHub organization"""

    ORG_URL = "https://api.github.com/orgs/{}"

    def __init__(self, org_name: str):
        """Initialize with organization name"""
        self.org_name = org_name

    @property
    def org(self) -> Dict:
        """Fetch the organization details"""
        return get_json(self.ORG_URL.format(self.org_name))

    @property
    def _public_repos_url(self) -> str:
        """Get the URL to the public repositories"""
        return self.org.get("repos_url")

    def public_repos(self, license: str = None) -> List[str]:
        """Get list of public repositories (optionally filtered by license)"""
        repos = get_json(self._public_repos_url)
        public_repos = [
            repo["name"] for repo in repos
            if not license or self.has_license(repo, license)
        ]
        return public_repos

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check if repo has a specific license"""
        return repo.get("license", {}).get("key") == license_key
