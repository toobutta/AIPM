"""GitHub API client utilities."""

import os
from typing import Dict, Any, Optional
import logging
import time
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize GitHub client."""
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        # Set headers
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'aipm-github-harvester/0.1.0'
        }
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        self.session.headers.update(headers)
    
    def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Get repository information from GitHub API."""
        owner, repo = self._parse_repo_url(repo_url)
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                logger.warning("GitHub API rate limit exceeded")
                time.sleep(60)  # Wait 1 minute and retry
                response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Map to our RepositoryMetadata format
                return {
                    'url': repo_url,
                    'name': data['name'],
                    'full_name': data['full_name'],
                    'owner': data['owner']['login'],
                    'description': data.get('description'),
                    'primary_language': data.get('language'),
                    'topics': data.get('topics', []),
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'size': data.get('size', 0),
                    'default_branch': data.get('default_branch', 'main'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'pushed_at': data.get('pushed_at'),
                    'license': data.get('license', {}).get('name') if data.get('license') else None,
                    'has_wiki': data.get('has_wiki', False),
                    'has_pages': data.get('has_pages', False),
                    'archived': data.get('archived', False),
                    'disabled': data.get('disabled', False),
                }
            else:
                logger.warning(f"Failed to get repo info for {repo_url}: {response.status_code}")
                return self._create_minimal_repo_info(repo_url, owner, repo)
                
        except Exception as e:
            logger.error(f"Error fetching repo info for {repo_url}: {e}")
            return self._create_minimal_repo_info(repo_url, owner, repo)
    
    def get_languages(self, repo_url: str) -> Dict[str, int]:
        """Get repository languages breakdown."""
        owner, repo = self._parse_repo_url(repo_url)
        
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching languages for {repo_url}: {e}")
        
        return {}
    
    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse GitHub repository URL to extract owner and repo name."""
        parsed = urlparse(repo_url)
        
        # Handle different URL formats
        if parsed.netloc == 'github.com':
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                # Remove .git suffix if present
                if repo.endswith('.git'):
                    repo = repo[:-4]
                return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def _create_minimal_repo_info(self, repo_url: str, owner: str, repo: str) -> Dict[str, Any]:
        """Create minimal repository info when API fails."""
        return {
            'url': repo_url,
            'name': repo,
            'full_name': f"{owner}/{repo}",
            'owner': owner,
            'description': None,
            'primary_language': None,
            'topics': [],
            'stars': 0,
            'forks': 0,
            'size': 0,
            'default_branch': 'main',
            'created_at': None,
            'updated_at': None,
            'pushed_at': None,
            'license': None,
            'has_wiki': False,
            'has_pages': False,
            'archived': False,
            'disabled': False,
        }