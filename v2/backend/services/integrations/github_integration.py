"""
GitHub Integration

Provides integration with GitHub API for repository management,
issues, pull requests, and code collaboration.
"""

import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_integration import BaseIntegration, IntegrationResult


class GitHubIntegration(BaseIntegration):
    """Integration with GitHub API."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.base_url = "https://api.github.com"
        self.token = config.get('token', '')
        self.owner = config.get('owner', '')
        self.repo = config.get('repo', '')

    def get_required_config_fields(self) -> List[str]:
        return ['token']

    async def test_connection(self) -> IntegrationResult:
        """Test connection to GitHub API."""
        return await self._make_request('GET', f"{self.base_url}/user")

    async def get_capabilities(self) -> List[str]:
        return [
            'list_repositories',
            'get_repository',
            'create_issue',
            'update_issue',
            'close_issue',
            'list_issues',
            'create_pull_request',
            'update_pull_request',
            'merge_pull_request',
            'list_pull_requests',
            'get_file_contents',
            'update_file',
            'create_branch',
            'delete_branch',
            'list_commits',
            'create_release',
            'list_releases',
            'get_repository_stats',
            'search_code',
            'search_issues'
        ]

    async def execute_operation(self, operation: str, **kwargs) -> IntegrationResult:
        """Execute a GitHub operation."""

        operations = {
            'list_repositories': self._list_repositories,
            'get_repository': self._get_repository,
            'create_issue': self._create_issue,
            'update_issue': self._update_issue,
            'close_issue': self._close_issue,
            'list_issues': self._list_issues,
            'create_pull_request': self._create_pull_request,
            'update_pull_request': self._update_pull_request,
            'merge_pull_request': self._merge_pull_request,
            'list_pull_requests': self._list_pull_requests,
            'get_file_contents': self._get_file_contents,
            'update_file': self._update_file,
            'create_branch': self._create_branch,
            'delete_branch': self._delete_branch,
            'list_commits': self._list_commits,
            'create_release': self._create_release,
            'list_releases': self._list_releases,
            'get_repository_stats': self._get_repository_stats,
            'search_code': self._search_code,
            'search_issues': self._search_issues
        }

        if operation not in operations:
            return IntegrationResult(
                success=False,
                error=f"Unknown operation: {operation}"
            )

        try:
            return await operations[operation](**kwargs)
        except Exception as e:
            return IntegrationResult(
                success=False,
                error=f"Operation failed: {str(e)}"
            )

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers with authentication."""
        headers = super()._get_default_headers()
        headers['Authorization'] = f'token {self.token}'
        return headers

    async def _list_repositories(self, **kwargs) -> IntegrationResult:
        """List repositories for the authenticated user or organization."""
        owner = kwargs.get('owner', self.owner)
        if owner:
            url = f"{self.base_url}/users/{owner}/repos"
        else:
            url = f"{self.base_url}/user/repos"

        params = {
            'sort': kwargs.get('sort', 'updated'),
            'direction': kwargs.get('direction', 'desc'),
            'per_page': min(kwargs.get('per_page', 30), 100)
        }

        return await self._make_request('GET', url, params=params)

    async def _get_repository(self, **kwargs) -> IntegrationResult:
        """Get repository information."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)

        if not owner or not repo:
            return IntegrationResult(
                success=False,
                error="Owner and repo are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}"
        return await self._make_request('GET', url)

    async def _create_issue(self, **kwargs) -> IntegrationResult:
        """Create a new issue."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        title = kwargs.get('title')
        body = kwargs.get('body', '')
        labels = kwargs.get('labels', [])
        assignees = kwargs.get('assignees', [])

        if not owner or not repo or not title:
            return IntegrationResult(
                success=False,
                error="Owner, repo, and title are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        data = {
            'title': title,
            'body': body,
            'labels': labels,
            'assignees': assignees
        }

        return await self._make_request('POST', url, json=data)

    async def _update_issue(self, **kwargs) -> IntegrationResult:
        """Update an existing issue."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        issue_number = kwargs.get('issue_number')
        title = kwargs.get('title')
        body = kwargs.get('body')
        state = kwargs.get('state')
        labels = kwargs.get('labels')
        assignees = kwargs.get('assignees')

        if not owner or not repo or not issue_number:
            return IntegrationResult(
                success=False,
                error="Owner, repo, and issue_number are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"

        data = {}
        if title is not None:
            data['title'] = title
        if body is not None:
            data['body'] = body
        if state is not None:
            data['state'] = state
        if labels is not None:
            data['labels'] = labels
        if assignees is not None:
            data['assignees'] = assignees

        return await self._make_request('PATCH', url, json=data)

    async def _close_issue(self, **kwargs) -> IntegrationResult:
        """Close an issue."""
        kwargs['state'] = 'closed'
        return await self._update_issue(**kwargs)

    async def _list_issues(self, **kwargs) -> IntegrationResult:
        """List issues in a repository."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        state = kwargs.get('state', 'open')
        labels = kwargs.get('labels', [])
        assignee = kwargs.get('assignee')
        creator = kwargs.get('creator')

        if not owner or not repo:
            return IntegrationResult(
                success=False,
                error="Owner and repo are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            'state': state,
            'per_page': min(kwargs.get('per_page', 30), 100),
            'page': kwargs.get('page', 1)
        }

        if labels:
            params['labels'] = ','.join(labels)
        if assignee:
            params['assignee'] = assignee
        if creator:
            params['creator'] = creator

        return await self._make_request('GET', url, params=params)

    async def _create_pull_request(self, **kwargs) -> IntegrationResult:
        """Create a pull request."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        title = kwargs.get('title')
        head = kwargs.get('head')  # branch to merge from
        base = kwargs.get('base', 'main')  # branch to merge into
        body = kwargs.get('body', '')

        if not owner or not repo or not title or not head:
            return IntegrationResult(
                success=False,
                error="Owner, repo, title, and head branch are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body
        }

        return await self._make_request('POST', url, json=data)

    async def _merge_pull_request(self, **kwargs) -> IntegrationResult:
        """Merge a pull request."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        pull_number = kwargs.get('pull_number')
        commit_title = kwargs.get('commit_title')
        commit_message = kwargs.get('commit_message')
        merge_method = kwargs.get('merge_method', 'merge')  # merge, squash, rebase

        if not owner or not repo or not pull_number:
            return IntegrationResult(
                success=False,
                error="Owner, repo, and pull_number are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pull_number}/merge"
        data = {
            'commit_title': commit_title,
            'commit_message': commit_message,
            'merge_method': merge_method
        }

        return await self._make_request('PUT', url, json=data)

    async def _list_pull_requests(self, **kwargs) -> IntegrationResult:
        """List pull requests."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        state = kwargs.get('state', 'open')
        head = kwargs.get('head')
        base = kwargs.get('base')

        if not owner or not repo:
            return IntegrationResult(
                success=False,
                error="Owner and repo are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {
            'state': state,
            'per_page': min(kwargs.get('per_page', 30), 100),
            'page': kwargs.get('page', 1)
        }

        if head:
            params['head'] = head
        if base:
            params['base'] = base

        return await self._make_request('GET', url, params=params)

    async def _get_file_contents(self, **kwargs) -> IntegrationResult:
        """Get contents of a file."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        path = kwargs.get('path')
        ref = kwargs.get('ref', 'main')  # branch/tag/sha

        if not owner or not repo or not path:
            return IntegrationResult(
                success=False,
                error="Owner, repo, and path are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': ref}

        result = await self._make_request('GET', url, params=params)

        if result.success and result.data:
            # Decode base64 content if it's a file
            if isinstance(result.data, dict) and 'content' in result.data:
                try:
                    result.data['decoded_content'] = base64.b64decode(result.data['content']).decode('utf-8')
                except Exception as e:
                    result.data['decode_error'] = str(e)

        return result

    async def _update_file(self, **kwargs) -> IntegrationResult:
        """Update a file in the repository."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        path = kwargs.get('path')
        message = kwargs.get('message', 'Update file')
        content = kwargs.get('content')
        branch = kwargs.get('branch', 'main')
        sha = kwargs.get('sha')  # required for updates

        if not owner or not repo or not path or not content:
            return IntegrationResult(
                success=False,
                error="Owner, repo, path, and content are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        data = {
            'message': message,
            'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
            'branch': branch
        }

        if sha:
            data['sha'] = sha

        return await self._make_request('PUT', url, json=data)

    async def _create_branch(self, **kwargs) -> IntegrationResult:
        """Create a new branch."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        branch_name = kwargs.get('branch_name')
        source_sha = kwargs.get('source_sha')  # SHA to branch from

        if not owner or not repo or not branch_name or not source_sha:
            return IntegrationResult(
                success=False,
                error="Owner, repo, branch_name, and source_sha are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': source_sha
        }

        return await self._make_request('POST', url, json=data)

    async def _list_commits(self, **kwargs) -> IntegrationResult:
        """List commits in a repository."""
        owner = kwargs.get('owner', self.owner)
        repo = kwargs.get('repo', self.repo)
        sha = kwargs.get('sha')  # branch/commit SHA
        path = kwargs.get('path')  # filter by path
        author = kwargs.get('author')

        if not owner or not repo:
            return IntegrationResult(
                success=False,
                error="Owner and repo are required"
            )

        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            'per_page': min(kwargs.get('per_page', 30), 100),
            'page': kwargs.get('page', 1)
        }

        if sha:
            params['sha'] = sha
        if path:
            params['path'] = path
        if author:
            params['author'] = author

        return await self._make_request('GET', url, params=params)

    async def _search_code(self, **kwargs) -> IntegrationResult:
        """Search for code in repositories."""
        query = kwargs.get('query')
        repo = kwargs.get('repo')
        language = kwargs.get('language')
        filename = kwargs.get('filename')

        if not query:
            return IntegrationResult(
                success=False,
                error="Query is required"
            )

        url = f"{self.base_url}/search/code"
        params = {
            'q': query,
            'per_page': min(kwargs.get('per_page', 30), 100),
            'page': kwargs.get('page', 1)
        }

        if repo:
            params['q'] += f' repo:{repo}'
        if language:
            params['q'] += f' language:{language}'
        if filename:
            params['q'] += f' filename:{filename}'

        return await self._make_request('GET', url, params=params)

    async def _search_issues(self, **kwargs) -> IntegrationResult:
        """Search for issues and pull requests."""
        query = kwargs.get('query')
        repo = kwargs.get('repo')
        state = kwargs.get('state', 'open')
        labels = kwargs.get('labels', [])

        if not query:
            return IntegrationResult(
                success=False,
                error="Query is required"
            )

        url = f"{self.base_url}/search/issues"
        params = {
            'q': query,
            'per_page': min(kwargs.get('per_page', 30), 100),
            'page': kwargs.get('page', 1)
        }

        if repo:
            params['q'] += f' repo:{repo}'
        if state:
            params['q'] += f' state:{state}'
        if labels:
            params['q'] += f' label:"{" label:".join(labels)}"'

        return await self._make_request('GET', url, params=params)
