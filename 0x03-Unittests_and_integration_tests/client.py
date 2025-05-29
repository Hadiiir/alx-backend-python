"""GitHub client for testing examples"""

from utils import get_json, memoize


class GithubOrgClient:
    """A client for GitHub organization API"""
    
    ORG_URL = "https://api.github.com/orgs/{org}"
    
    def __init__(self, org_name):
        self._org_name = org_name
    
    @memoize
    def org(self):
        """Get organization information"""
        url = self.ORG_URL.format(org=self._org_name)
        return get_json(url)
    
    @property
    def _public_repos_url(self):
        """Get the public repos URL from org data"""
        return self.org()["repos_url"]
    
    def public_repos(self, license=None):
        """Get list of public repositories"""
        repos_url = self._public_repos_url
        repos_data = get_json(repos_url)
        
        repos = [repo["name"] for repo in repos_data]
        
        if license:
            repos = [
                repo_name for repo_name, repo_data in zip(repos, repos_data)
                if self.has_license(repo_data, license)
            ]
        
        return repos
    
    @staticmethod
    def has_license(repo, license_key):
        """Check if repository has specific license"""
        license_info = repo.get("license")
        if license_info:
            return license_info.get("key") == license_key
        return False


# Example usage
if __name__ == "__main__":
    print("GitHub Client Example:")
    
    # This would normally make real API calls
    # In tests, we'll mock these calls
    try:
        client = GithubOrgClient("google")
        print(f"Created client for: {client._org_name}")
        print("Note: In real usage, this would make API calls")
        print("In tests, we mock these calls to avoid external dependencies")
    except Exception as e:
        print(f"Expected error in example (no mocking): {e}")