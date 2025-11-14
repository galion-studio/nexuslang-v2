"""
Slack Integration

Provides integration with Slack API for team communication,
channel management, and automated messaging.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_integration import BaseIntegration, IntegrationResult


class SlackIntegration(BaseIntegration):
    """Integration with Slack API."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.base_url = "https://slack.com/api"
        self.token = config.get('token', '')
        self.default_channel = config.get('default_channel', '')

    def get_required_config_fields(self) -> List[str]:
        return ['token']

    async def test_connection(self) -> IntegrationResult:
        """Test connection to Slack API."""
        return await self._make_request('POST', f"{self.base_url}/auth.test")

    async def get_capabilities(self) -> List[str]:
        return [
            'send_message',
            'send_formatted_message',
            'create_channel',
            'invite_to_channel',
            'list_channels',
            'get_channel_info',
            'upload_file',
            'search_messages',
            'get_user_info',
            'list_users',
            'create_reminder',
            'schedule_message',
            'update_message',
            'delete_message',
            'get_conversation_history',
            'get_thread_replies',
            'add_reaction',
            'remove_reaction'
        ]

    async def execute_operation(self, operation: str, **kwargs) -> IntegrationResult:
        """Execute a Slack operation."""

        operations = {
            'send_message': self._send_message,
            'send_formatted_message': self._send_formatted_message,
            'create_channel': self._create_channel,
            'invite_to_channel': self._invite_to_channel,
            'list_channels': self._list_channels,
            'get_channel_info': self._get_channel_info,
            'upload_file': self._upload_file,
            'search_messages': self._search_messages,
            'get_user_info': self._get_user_info,
            'list_users': self._list_users,
            'create_reminder': self._create_reminder,
            'schedule_message': self._schedule_message,
            'update_message': self._update_message,
            'delete_message': self._delete_message,
            'get_conversation_history': self._get_conversation_history,
            'get_thread_replies': self._get_thread_replies,
            'add_reaction': self._add_reaction,
            'remove_reaction': self._remove_reaction
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
        headers['Authorization'] = f'Bearer {self.token}'
        return headers

    async def _send_message(self, **kwargs) -> IntegrationResult:
        """Send a simple text message."""
        channel = kwargs.get('channel', self.default_channel)
        text = kwargs.get('text', '')
        thread_ts = kwargs.get('thread_ts')  # for replying in threads

        if not channel or not text:
            return IntegrationResult(
                success=False,
                error="Channel and text are required"
            )

        url = f"{self.base_url}/chat.postMessage"
        data = {
            'channel': channel,
            'text': text
        }

        if thread_ts:
            data['thread_ts'] = thread_ts

        return await self._make_request('POST', url, json=data)

    async def _send_formatted_message(self, **kwargs) -> IntegrationResult:
        """Send a formatted message with blocks and attachments."""
        channel = kwargs.get('channel', self.default_channel)
        blocks = kwargs.get('blocks', [])
        attachments = kwargs.get('attachments', [])
        text = kwargs.get('text', 'Message')
        thread_ts = kwargs.get('thread_ts')

        if not channel:
            return IntegrationResult(
                success=False,
                error="Channel is required"
            )

        if not blocks and not attachments and not text:
            return IntegrationResult(
                success=False,
                error="Blocks, attachments, or text are required"
            )

        url = f"{self.base_url}/chat.postMessage"
        data = {
            'channel': channel,
            'text': text
        }

        if blocks:
            data['blocks'] = blocks
        if attachments:
            data['attachments'] = attachments
        if thread_ts:
            data['thread_ts'] = thread_ts

        return await self._make_request('POST', url, json=data)

    async def _create_channel(self, **kwargs) -> IntegrationResult:
        """Create a new channel."""
        name = kwargs.get('name')
        is_private = kwargs.get('is_private', False)
        description = kwargs.get('description', '')

        if not name:
            return IntegrationResult(
                success=False,
                error="Channel name is required"
            )

        url = f"{self.base_url}/conversations.create"
        data = {
            'name': name,
            'is_private': is_private
        }

        if description:
            data['purpose'] = description

        result = await self._make_request('POST', url, json=data)

        # Set topic if provided
        if result.success and description:
            channel_id = result.data.get('channel', {}).get('id')
            if channel_id:
                await self._set_channel_topic(channel_id, description)

        return result

    async def _invite_to_channel(self, **kwargs) -> IntegrationResult:
        """Invite users to a channel."""
        channel = kwargs.get('channel')
        users = kwargs.get('users', [])  # list of user IDs

        if not channel or not users:
            return IntegrationResult(
                success=False,
                error="Channel and users are required"
            )

        url = f"{self.base_url}/conversations.invite"
        data = {
            'channel': channel,
            'users': ','.join(users) if isinstance(users, list) else users
        }

        return await self._make_request('POST', url, json=data)

    async def _list_channels(self, **kwargs) -> IntegrationResult:
        """List channels in the workspace."""
        types = kwargs.get('types', 'public_channel,private_channel')
        exclude_archived = kwargs.get('exclude_archived', True)

        url = f"{self.base_url}/conversations.list"
        params = {
            'types': types,
            'exclude_archived': exclude_archived,
            'limit': min(kwargs.get('limit', 100), 1000)
        }

        return await self._make_request('GET', url, params=params)

    async def _get_channel_info(self, **kwargs) -> IntegrationResult:
        """Get information about a channel."""
        channel = kwargs.get('channel')

        if not channel:
            return IntegrationResult(
                success=False,
                error="Channel is required"
            )

        url = f"{self.base_url}/conversations.info"
        params = {'channel': channel}

        return await self._make_request('GET', url, params=params)

    async def _upload_file(self, **kwargs) -> IntegrationResult:
        """Upload a file to Slack."""
        channels = kwargs.get('channels', [self.default_channel])
        filename = kwargs.get('filename')
        content = kwargs.get('content')  # file content or URL
        title = kwargs.get('title')
        initial_comment = kwargs.get('initial_comment')

        if not channels or not filename or not content:
            return IntegrationResult(
                success=False,
                error="Channels, filename, and content are required"
            )

        url = f"{self.base_url}/files.upload"
        data = {
            'channels': ','.join(channels) if isinstance(channels, list) else channels,
            'filename': filename
        }

        if title:
            data['title'] = title
        if initial_comment:
            data['initial_comment'] = initial_comment

        # Handle file content
        if isinstance(content, str) and (content.startswith('http://') or content.startswith('https://')):
            data['url_private'] = content
        else:
            data['content'] = content

        return await self._make_request('POST', url, data=data)

    async def _search_messages(self, **kwargs) -> IntegrationResult:
        """Search for messages."""
        query = kwargs.get('query')
        channel = kwargs.get('channel')
        user = kwargs.get('user')

        if not query:
            return IntegrationResult(
                success=False,
                error="Query is required"
            )

        url = f"{self.base_url}/search.messages"
        params = {
            'query': query,
            'count': min(kwargs.get('count', 20), 100),
            'page': kwargs.get('page', 1)
        }

        if channel:
            params['query'] += f' in:{channel}'
        if user:
            params['query'] += f' from:{user}'

        return await self._make_request('GET', url, params=params)

    async def _get_user_info(self, **kwargs) -> IntegrationResult:
        """Get information about a user."""
        user = kwargs.get('user')

        if not user:
            return IntegrationResult(
                success=False,
                error="User ID is required"
            )

        url = f"{self.base_url}/users.info"
        params = {'user': user}

        return await self._make_request('GET', url, params=params)

    async def _list_users(self, **kwargs) -> IntegrationResult:
        """List users in the workspace."""
        url = f"{self.base_url}/users.list"
        params = {
            'limit': min(kwargs.get('limit', 100), 1000),
            'presence': kwargs.get('presence', False)
        }

        return await self._make_request('GET', url, params=params)

    async def _create_reminder(self, **kwargs) -> IntegrationResult:
        """Create a reminder."""
        text = kwargs.get('text')
        time = kwargs.get('time')  # timestamp or natural language
        user = kwargs.get('user')

        if not text or not time:
            return IntegrationResult(
                success=False,
                error="Text and time are required"
            )

        url = f"{self.base_url}/reminders.add"
        data = {
            'text': text,
            'time': time
        }

        if user:
            data['user'] = user

        return await self._make_request('POST', url, json=data)

    async def _schedule_message(self, **kwargs) -> IntegrationResult:
        """Schedule a message to be sent later."""
        channel = kwargs.get('channel', self.default_channel)
        text = kwargs.get('text')
        post_at = kwargs.get('post_at')  # Unix timestamp

        if not channel or not text or not post_at:
            return IntegrationResult(
                success=False,
                error="Channel, text, and post_at timestamp are required"
            )

        url = f"{self.base_url}/chat.scheduleMessage"
        data = {
            'channel': channel,
            'text': text,
            'post_at': int(post_at)
        }

        return await self._make_request('POST', url, json=data)

    async def _update_message(self, **kwargs) -> IntegrationResult:
        """Update a message."""
        channel = kwargs.get('channel')
        ts = kwargs.get('ts')  # timestamp of message to update
        text = kwargs.get('text')
        blocks = kwargs.get('blocks')

        if not channel or not ts:
            return IntegrationResult(
                success=False,
                error="Channel and timestamp are required"
            )

        if not text and not blocks:
            return IntegrationResult(
                success=False,
                error="Text or blocks are required"
            )

        url = f"{self.base_url}/chat.update"
        data = {
            'channel': channel,
            'ts': ts
        }

        if text:
            data['text'] = text
        if blocks:
            data['blocks'] = blocks

        return await self._make_request('POST', url, json=data)

    async def _delete_message(self, **kwargs) -> IntegrationResult:
        """Delete a message."""
        channel = kwargs.get('channel')
        ts = kwargs.get('ts')  # timestamp of message to delete

        if not channel or not ts:
            return IntegrationResult(
                success=False,
                error="Channel and timestamp are required"
            )

        url = f"{self.base_url}/chat.delete"
        data = {
            'channel': channel,
            'ts': ts
        }

        return await self._make_request('POST', url, json=data)

    async def _get_conversation_history(self, **kwargs) -> IntegrationResult:
        """Get conversation history."""
        channel = kwargs.get('channel')
        limit = kwargs.get('limit', 100)

        if not channel:
            return IntegrationResult(
                success=False,
                error="Channel is required"
            )

        url = f"{self.base_url}/conversations.history"
        params = {
            'channel': channel,
            'limit': min(limit, 200)
        }

        return await self._make_request('GET', url, params=params)

    async def _get_thread_replies(self, **kwargs) -> IntegrationResult:
        """Get replies in a thread."""
        channel = kwargs.get('channel')
        ts = kwargs.get('ts')  # timestamp of parent message

        if not channel or not ts:
            return IntegrationResult(
                success=False,
                error="Channel and timestamp are required"
            )

        url = f"{self.base_url}/conversations.replies"
        params = {
            'channel': channel,
            'ts': ts,
            'limit': min(kwargs.get('limit', 200), 200)
        }

        return await self._make_request('GET', url, params=params)

    async def _add_reaction(self, **kwargs) -> IntegrationResult:
        """Add a reaction to a message."""
        channel = kwargs.get('channel')
        timestamp = kwargs.get('timestamp')
        name = kwargs.get('name')  # emoji name

        if not channel or not timestamp or not name:
            return IntegrationResult(
                success=False,
                error="Channel, timestamp, and emoji name are required"
            )

        url = f"{self.base_url}/reactions.add"
        data = {
            'channel': channel,
            'timestamp': timestamp,
            'name': name
        }

        return await self._make_request('POST', url, json=data)

    async def _remove_reaction(self, **kwargs) -> IntegrationResult:
        """Remove a reaction from a message."""
        channel = kwargs.get('channel')
        timestamp = kwargs.get('timestamp')
        name = kwargs.get('name')  # emoji name

        if not channel or not timestamp or not name:
            return IntegrationResult(
                success=False,
                error="Channel, timestamp, and emoji name are required"
            )

        url = f"{self.base_url}/reactions.remove"
        data = {
            'channel': channel,
            'timestamp': timestamp,
            'name': name
        }

        return await self._make_request('POST', url, json=data)

    async def _set_channel_topic(self, channel: str, topic: str) -> IntegrationResult:
        """Set channel topic (helper method)."""
        url = f"{self.base_url}/conversations.setTopic"
        data = {
            'channel': channel,
            'topic': topic
        }

        return await self._make_request('POST', url, json=data)
