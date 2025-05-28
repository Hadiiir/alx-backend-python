#!/usr/bin/env python3
"""A github org client"""
from typing import List, Dict
from utils import get_json, memoize

class GithubOrgClient:
    """A Github org client"""
    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Init method"""
        self._org_name = org_name
        self._org = None

    @property
    def org(self) -> Dict:
        """Get org data"""
        if self._org is None:
            self._org = get_json(self.ORG_URL.format(org=self._org_name))
        return self._org

    @property
    def _public_repos_url(self) -> str:
        """Public repos URL"""
        return self.org["repos_url"]

    @property
    def repos_payload(self) -> Dict:
        """Get repos payload"""
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """Public repos"""
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]
        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """Static: has_license"""
        assert license_key is not None, "license_key cannot be None"
        try:
            return repo["license"]["key"] == license_key
        except KeyError:
            return False