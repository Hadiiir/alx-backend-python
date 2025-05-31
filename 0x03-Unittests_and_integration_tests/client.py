"""
GitHub organization client
"""

from utils import get_json, memoize


class GithubOrgClient:
    """A client for GitHub organization data"""
    
    ORG_URL = "https://api.github.com/orgs/{org}"
    
    def __init__(self, org_name):
        self._org_name = org_name
    
    @memoize
    def org(self):
        """Get organization data"""
        return get_json(self.ORG_URL.format(org=self._org_name))
    
    @property
    def _public_repos_url(self):
        """Get the public repos URL from org data"""
        return self.org["repos_url"]
    
    def public_repos(self, license=None):
        """
        Get list of public repositories
        
        Args:
            license: Optional license filter
            
        Returns:
            List of repository names
        """
        repos_data = get_json(self._public_repos_url)
        repos = [repo["name"] for repo in repos_data]
        
        if license:
            repos = [
                repo["name"] for repo in repos_data 
                if self.has_license(repo, license)
            ]
        
        return repos
    
    @staticmethod
    def has_license(repo, license_key):
        """
        Check if repository has a specific license
        
        Args:
            repo: Repository data dictionary
            license_key: License key to check for
            
        Returns:
            True if repo has the license, False otherwise
        """
        license_info = repo.get("license")
        if license_info:
            return license_info.get("key") == license_key
        return False


# Demo usage
print("GitHub Client Demo:")
print("=" * 30)

# This would normally make HTTP requests, but we'll mock them in tests
try:
    client = GithubOrgClient("google")
    print(f"Created client for organization: google")
    print("Note: Actual API calls would be made here")
except Exception as e:
    print(f"Demo client created (would make API calls): {e}")