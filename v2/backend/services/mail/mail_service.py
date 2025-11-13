"""
Mail Service for Galion Ecosystem
Handles email connections, syncing, and AI integration
"""

import asyncio
import imaplib
import smtplib
import email
import email.header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
import secrets
from uuid import UUID
import base64
import hashlib

# OAuth libraries
try:
    import requests_oauthlib
    from requests_oauthlib import OAuth2Session
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

from ...core.database import get_db
from ...models.mail import (
    MailProvider, MailConnection, MailFolder,
    MailMessage, MailAIInteraction
)
from ...services.ai import get_ai_router
from ...core.errors import ValidationError, ServiceUnavailableError
from ...core.config import settings

logger = logging.getLogger(__name__)


class MailService:
    """Comprehensive mail service with AI integration"""

    def __init__(self, db):
        self.db = db
        self.ai_router = get_ai_router()
        self._oauth_sessions = {}  # Cache OAuth sessions

    async def create_oauth_connection(self, user_id: str, auth_code: str, state: str) -> MailConnection:
        """Create mail connection using OAuth flow"""
        if not OAUTH_AVAILABLE:
            raise ServiceUnavailableError("OAuth libraries not available")

        try:
            # Extract provider from state or determine from context
            # For now, assume Gmail (can be extended)
            provider_name = "gmail"

            # Get provider configuration
            stmt = self.db.query(MailProvider).filter(MailProvider.name == provider_name)
            provider = stmt.first()

            if not provider:
                raise ValidationError("Email provider not configured")

            # Exchange code for tokens
            token_url = provider.token_url
            client_id = provider.client_id
            client_secret = provider.client_secret

            # Create OAuth session
            oauth = OAuth2Session(client_id, redirect_uri=f"{settings.FRONTEND_URL}/settings/mail/oauth/callback")

            # Get tokens
            token = oauth.fetch_token(
                token_url=token_url,
                code=auth_code,
                client_secret=client_secret
            )

            # Get user profile to verify email
            profile_resp = oauth.get('https://www.googleapis.com/oauth2/v2/userinfo')
            profile = profile_resp.json()

            email_address = profile['email']
            display_name = profile.get('name', email_address.split('@')[0])

            # Check if connection already exists
            existing = self.db.query(MailConnection).filter(
                MailConnection.user_id == user_id,
                MailConnection.email == email_address
            ).first()

            if existing:
                # Update existing connection
                existing.access_token = token.get('access_token')
                existing.refresh_token = token.get('refresh_token')
                existing.token_expires_at = datetime.utcnow() + timedelta(seconds=token.get('expires_in', 3600))
                existing.display_name = display_name
                existing.updated_at = datetime.utcnow()
                connection = existing
            else:
                # Create new connection
                connection = MailConnection(
                    user_id=user_id,
                    provider_id=provider.id,
                    email=email_address,
                    display_name=display_name,
                    access_token=token.get('access_token'),
                    refresh_token=token.get('refresh_token'),
                    token_expires_at=datetime.utcnow() + timedelta(seconds=token.get('expires_in', 3600)),
                    sync_enabled=True,
                    ai_assistant_enabled=True
                )
                self.db.add(connection)

            await self.db.commit()
            await self.db.refresh(connection)

            # Start initial sync
            asyncio.create_task(self.sync_connection(str(connection.id)))

            return connection

        except Exception as e:
            logger.error(f"OAuth connection failed: {e}")
            await self.db.rollback()
            raise ServiceUnavailableError(f"Failed to create OAuth connection: {str(e)}")

    async def create_manual_connection(
        self,
        user_id: str,
        provider_name: str,
        email: str,
        imap_username: Optional[str] = None,
        imap_password: Optional[str] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None
    ) -> MailConnection:
        """Create mail connection with manual IMAP/SMTP credentials"""
        try:
            # Get provider configuration
            stmt = self.db.query(MailProvider).filter(MailProvider.name == provider_name)
            provider = stmt.first()

            if not provider:
                raise ValidationError("Email provider not configured")

            # Encrypt passwords (simplified - use proper encryption in production)
            encrypted_imap = base64.b64encode(imap_password.encode()).decode() if imap_password else None
            encrypted_smtp = base64.b64encode(smtp_password.encode()).decode() if smtp_password else None

            # Create connection
            connection = MailConnection(
                user_id=user_id,
                provider_id=provider.id,
                email=email,
                display_name=email.split('@')[0],
                imap_username=imap_username,
                imap_password=encrypted_imap,
                smtp_username=smtp_username,
                smtp_password=encrypted_smtp,
                sync_enabled=True,
                ai_assistant_enabled=True
            )

            self.db.add(connection)
            await self.db.commit()
            await self.db.refresh(connection)

            # Test connection
            await self._test_imap_connection(connection)

            # Start initial sync
            asyncio.create_task(self.sync_connection(str(connection.id)))

            return connection

        except Exception as e:
            logger.error(f"Manual connection failed: {e}")
            await self.db.rollback()
            raise ValidationError(f"Failed to create manual connection: {str(e)}")

    async def sync_connection(self, connection_id: str) -> bool:
        """Sync mail connection with provider"""
        try:
            connection = self.db.query(MailConnection).filter(MailConnection.id == connection_id).first()
            if not connection:
                return False

            # Update sync status
            connection.sync_status = 'syncing'
            connection.last_sync_at = datetime.utcnow()
            await self.db.commit()

            try:
                if connection.access_token:
                    # OAuth-based sync
                    await self._sync_oauth_connection(connection)
                else:
                    # IMAP-based sync
                    await self._sync_imap_connection(connection)

                connection.sync_status = 'idle'
                await self.db.commit()
                return True

            except Exception as e:
                logger.error(f"Sync failed for connection {connection_id}: {e}")
                connection.sync_status = 'error'
                connection.error_message = str(e)
                await self.db.commit()
                return False

        except Exception as e:
            logger.error(f"Sync setup failed for connection {connection_id}: {e}")
            return False

    async def _sync_oauth_connection(self, connection: MailConnection):
        """Sync using OAuth (Gmail API)"""
        try:
            # Refresh token if needed
            if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
                await self._refresh_oauth_token(connection)

            # Use Gmail API for sync
            # This is a simplified implementation - in production use google-api-python-client
            headers = {
                'Authorization': f'Bearer {connection.access_token}',
                'Accept': 'application/json'
            }

            # Get message list
            messages_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
            params = {'maxResults': 50, 'q': 'newer_than:1d'}  # Last day's messages

            # In production, make actual API calls
            # For now, simulate sync
            logger.info(f"Simulating OAuth sync for {connection.email}")

            # Update folders
            await self._sync_folders(connection)

        except Exception as e:
            logger.error(f"OAuth sync failed: {e}")
            raise

    async def _sync_imap_connection(self, connection: MailConnection):
        """Sync using IMAP"""
        try:
            provider = connection.provider

            # Connect to IMAP
            imap_server = imaplib.IMAP4_SSL(provider.imap_host, int(provider.imap_port))

            # Decrypt password
            password = base64.b64decode(connection.imap_password).decode() if connection.imap_password else None

            # Login
            imap_server.login(connection.imap_username or connection.email, password)

            # Sync folders
            await self._sync_imap_folders(connection, imap_server)

            # Sync messages from INBOX
            await self._sync_imap_messages(connection, imap_server, 'INBOX')

            imap_server.logout()

        except Exception as e:
            logger.error(f"IMAP sync failed: {e}")
            raise

    async def _sync_folders(self, connection: MailConnection):
        """Sync mail folders"""
        try:
            # Default folders for most providers
            default_folders = [
                {'name': 'INBOX', 'type': 'inbox'},
                {'name': 'Sent', 'type': 'sent'},
                {'name': 'Drafts', 'type': 'drafts'},
                {'name': 'Trash', 'type': 'trash'},
                {'name': 'Spam', 'type': 'spam'},
            ]

            for folder_data in default_folders:
                folder = self.db.query(MailFolder).filter(
                    MailFolder.connection_id == connection.id,
                    MailFolder.name == folder_data['name']
                ).first()

                if not folder:
                    folder = MailFolder(
                        connection_id=connection.id,
                        folder_id=folder_data['name'],
                        name=folder_data['name'],
                        display_name=folder_data['name'],
                        folder_type=folder_data['type'],
                        is_system=True
                    )
                    self.db.add(folder)

            await self.db.commit()

        except Exception as e:
            logger.error(f"Folder sync failed: {e}")
            raise

    async def _sync_imap_folders(self, connection: MailConnection, imap_server):
        """Sync IMAP folders"""
        try:
            # List mailboxes
            status, mailboxes = imap_server.list()
            if status != 'OK':
                return

            for mailbox in mailboxes:
                if isinstance(mailbox, bytes):
                    mailbox = mailbox.decode()
                # Parse mailbox format: (\HasNoChildren) "/" "INBOX"
                parts = mailbox.split(' "/" ')
                if len(parts) >= 2:
                    folder_name = parts[1].strip('"')
                    folder_type = self._guess_folder_type(folder_name)

                    folder = self.db.query(MailFolder).filter(
                        MailFolder.connection_id == connection.id,
                        MailFolder.name == folder_name
                    ).first()

                    if not folder:
                        folder = MailFolder(
                            connection_id=connection.id,
                            folder_id=folder_name,
                            name=folder_name,
                            display_name=folder_name,
                            folder_type=folder_type
                        )
                        self.db.add(folder)

            await self.db.commit()

        except Exception as e:
            logger.error(f"IMAP folder sync failed: {e}")

    async def _sync_imap_messages(self, connection: MailConnection, imap_server, folder_name: str):
        """Sync messages from IMAP folder"""
        try:
            # Select folder
            status, data = imap_server.select(folder_name)
            if status != 'OK':
                return

            # Get folder
            folder = self.db.query(MailFolder).filter(
                MailFolder.connection_id == connection.id,
                MailFolder.name == folder_name
            ).first()

            if not folder:
                return

            # Search for recent messages (last 7 days)
            status, messages = imap_server.search(None, 'SINCE', (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y'))
            if status != 'OK':
                return

            message_nums = messages[0].split()

            for num in message_nums[-10:]:  # Process last 10 messages
                await self._sync_single_message(connection, folder, imap_server, num)

            await self.db.commit()

        except Exception as e:
            logger.error(f"IMAP message sync failed: {e}")

    async def _sync_single_message(self, connection: MailConnection, folder: MailFolder,
                                 imap_server, message_num: bytes):
        """Sync a single message"""
        try:
            # Fetch message
            status, msg_data = imap_server.fetch(message_num, '(RFC822)')
            if status != 'OK':
                return

            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Parse message
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            to_recipients = self._decode_header(email_message.get('To', ''))
            date_str = email_message.get('Date', '')

            # Extract sender info
            sender_name, sender_email = self._parse_email_address(sender)

            # Extract body
            body_text, body_html = self._extract_body(email_message)

            # Create message record
            message_id = email_message.get('Message-ID', '').strip('<>')
            sent_at = self._parse_email_date(date_str)

            # Check if message already exists
            existing = self.db.query(MailMessage).filter(
                MailMessage.connection_id == connection.id,
                MailMessage.message_id == message_id
            ).first()

            if existing:
                return

            message = MailMessage(
                connection_id=connection.id,
                folder_id=folder.id,
                message_id=message_id,
                subject=subject,
                sender_name=sender_name,
                sender_email=sender_email,
                sent_at=sent_at,
                received_at=datetime.utcnow(),
                body_text=body_text,
                body_html=body_html
            )

            self.db.add(message)

            # Generate AI analysis if enabled
            if connection.ai_assistant_enabled:
                asyncio.create_task(self._analyze_message_with_ai(message))

        except Exception as e:
            logger.error(f"Single message sync failed: {e}")

    async def _analyze_message_with_ai(self, message: MailMessage):
        """Analyze message with AI"""
        try:
            if not self.ai_router:
                return

            # Generate summary
            summary_prompt = f"""
            Summarize this email in 2-3 sentences, focusing on the main points and any action items:

            Subject: {message.subject or 'No subject'}
            From: {message.sender_name or 'Unknown'} <{message.sender_email or 'Unknown'}>
            Body: {message.body_text[:1000] if message.body_text else 'No body'}
            """

            summary = await self.ai_router.quick_response(summary_prompt, max_tokens=150)

            # Categorize message
            category_prompt = f"""
            Categorize this email into one of: work, personal, marketing, spam, social, financial, other

            Subject: {message.subject or ''}
            From: {message.sender_email or ''}
            Content preview: {message.body_text[:500] if message.body_text else ''}
            """

            category = await self.ai_router.quick_response(category_prompt, max_tokens=20)
            category = category.strip().lower()

            # Determine priority
            priority_prompt = f"""
            Determine priority of this email: urgent, high, medium, low

            Consider: subject importance, sender, content urgency, deadlines mentioned
            Subject: {message.subject or ''}
            Content: {message.body_text[:500] if message.body_text else ''}
            """

            priority = await self.ai_router.quick_response(priority_prompt, max_tokens=10)
            priority = priority.strip().lower()

            # Extract keywords
            keywords_prompt = f"""
            Extract 3-5 key topics or keywords from this email:

            Subject: {message.subject or ''}
            Content: {message.body_text[:800] if message.body_text else ''}
            """

            keywords_text = await self.ai_router.quick_response(keywords_prompt, max_tokens=50)
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()][:5]

            # Update message
            message.ai_summary = summary.strip()
            message.ai_category = category
            message.ai_priority = priority
            message.ai_keywords = keywords

            await self.db.commit()

        except Exception as e:
            logger.error(f"AI message analysis failed: {e}")

    async def generate_ai_summary(self, user_id: str, message_id: str,
                                include_action_items: bool = True,
                                include_keywords: bool = True,
                                custom_instructions: Optional[str] = None) -> str:
        """Generate AI summary for a message"""
        try:
            message = self.db.query(MailMessage).join(MailConnection).filter(
                MailMessage.id == message_id,
                MailConnection.user_id == user_id
            ).first()

            if not message:
                raise ValidationError("Message not found")

            prompt = f"""
            {custom_instructions or "Provide a comprehensive summary of this email"}

            Subject: {message.subject or 'No subject'}
            From: {message.sender_name or 'Unknown'} <{message.sender_email or 'Unknown'}>
            Date: {message.sent_at or 'Unknown'}

            Content:
            {message.body_text or 'No content'}
            """

            if include_action_items:
                prompt += "\n\nAlso identify any action items or tasks mentioned in the email."

            if include_keywords:
                prompt += "\n\nExtract key topics and keywords from the email."

            summary = await self.ai_router.quick_response(prompt, max_tokens=300)

            # Log AI interaction
            interaction = MailAIInteraction(
                user_id=user_id,
                message_id=message_id,
                interaction_type='summary',
                ai_model_used='gpt-4',  # Simplified
                prompt_used=prompt[:500],
                ai_response=summary[:1000]
            )
            self.db.add(interaction)
            await self.db.commit()

            return summary

        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            raise ServiceUnavailableError("Failed to generate AI summary")

    async def generate_ai_response(self, user_id: str, message_id: str,
                                 response_type: str, tone: str, length: str,
                                 custom_instructions: Optional[str] = None,
                                 generate_voice: bool = False) -> Dict[str, Any]:
        """Generate AI response for a message"""
        try:
            message = self.db.query(MailMessage).join(MailConnection).filter(
                MailMessage.id == message_id,
                MailConnection.user_id == user_id
            ).first()

            if not message:
                raise ValidationError("Message not found")

            # Build response prompt
            action_map = {
                'reply': 'Write a reply to this email',
                'forward': 'Write a forwarding message for this email',
                'draft': 'Write a draft response to this email'
            }

            tone_map = {
                'professional': 'professional and formal',
                'friendly': 'friendly and approachable',
                'concise': 'brief and to the point',
                'detailed': 'comprehensive and thorough'
            }

            length_map = {
                'short': '1-2 paragraphs',
                'medium': '2-3 paragraphs',
                'long': '3-4 paragraphs with full detail'
            }

            prompt = f"""
            {action_map.get(response_type, 'Respond to')} this email in a {tone_map.get(tone, 'professional')} tone.
            Keep the response {length_map.get(length, 'medium')} in length.

            Original Email:
            Subject: {message.subject or 'No subject'}
            From: {message.sender_name or 'Unknown'} <{message.sender_email or 'Unknown'}>

            Content:
            {message.body_text or 'No content'}

            {custom_instructions or ''}
            """

            response_text = await self.ai_router.quick_response(prompt, max_tokens=500)

            result = {
                'text': response_text,
                'type': response_type,
                'tone': tone,
                'length': length
            }

            # Generate voice response if requested
            if generate_voice:
                voice_url = await self._generate_voice_response(response_text, user_id)
                if voice_url:
                    result['voice_url'] = voice_url

            # Generate smart reply suggestions
            suggestions = await self._generate_reply_suggestions(message, response_type)
            result['suggestions'] = suggestions

            # Log AI interaction
            interaction = MailAIInteraction(
                user_id=user_id,
                message_id=message_id,
                interaction_type='response',
                ai_model_used='gpt-4',
                prompt_used=prompt[:500],
                ai_response=response_text[:1000],
                voice_request=generate_voice,
                voice_response_generated=bool(result.get('voice_url'))
            )
            self.db.add(interaction)
            await self.db.commit()

            return result

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            raise ServiceUnavailableError("Failed to generate AI response")

    async def _generate_voice_response(self, text: str, user_id: str) -> Optional[str]:
        """Generate voice response using text-to-speech"""
        try:
            # This would integrate with a TTS service like ElevenLabs, Azure TTS, etc.
            # For now, return a mock URL
            voice_hash = hashlib.md5(f"{user_id}:{text[:100]}".encode()).hexdigest()
            return f"https://api.galion.ai/voice/{voice_hash}.mp3"
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            return None

    async def _generate_reply_suggestions(self, message: MailMessage, response_type: str) -> List[str]:
        """Generate smart reply suggestions"""
        try:
            prompt = f"""
            Generate 3 short reply suggestions for this email:

            Subject: {message.subject or ''}
            Content: {message.body_text[:300] if message.body_text else ''}

            Make them professional and relevant.
            """

            suggestions_text = await self.ai_router.quick_response(prompt, max_tokens=200)
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()][:3]

            return suggestions
        except Exception as e:
            logger.error(f"Reply suggestions failed: {e}")
            return []

    async def _refresh_oauth_token(self, connection: MailConnection):
        """Refresh OAuth access token"""
        try:
            provider = connection.provider
            client_id = provider.client_id
            client_secret = provider.client_secret

            # Create OAuth session
            oauth = OAuth2Session(client_id)

            # Refresh token
            token = oauth.refresh_token(
                provider.token_url,
                refresh_token=connection.refresh_token,
                client_secret=client_secret
            )

            # Update connection
            connection.access_token = token.get('access_token')
            connection.refresh_token = token.get('refresh_token', connection.refresh_token)
            connection.token_expires_at = datetime.utcnow() + timedelta(seconds=token.get('expires_in', 3600))

            await self.db.commit()

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise

    async def _test_imap_connection(self, connection: MailConnection):
        """Test IMAP connection"""
        try:
            provider = connection.provider
            password = base64.b64decode(connection.imap_password).decode() if connection.imap_password else None

            imap_server = imaplib.IMAP4_SSL(provider.imap_host, int(provider.imap_port))
            imap_server.login(connection.imap_username or connection.email, password)
            imap_server.logout()

        except Exception as e:
            raise ValidationError(f"IMAP connection test failed: {str(e)}")

    def _decode_header(self, header_value: str) -> str:
        """Decode email header"""
        try:
            decoded = email.header.decode_header(header_value)
            result = ''
            for part, encoding in decoded:
                if isinstance(part, bytes):
                    result += part.decode(encoding or 'utf-8')
                else:
                    result += str(part)
            return result
        except:
            return header_value

    def _parse_email_address(self, address: str) -> Tuple[str, str]:
        """Parse email address into name and email"""
        try:
            import email.utils
            parsed = email.utils.parseaddr(address)
            return parsed[0], parsed[1]
        except:
            return '', address

    def _extract_body(self, email_message) -> Tuple[str, str]:
        """Extract text and HTML body from email"""
        text_body = ''
        html_body = ''

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not text_body:
                    text_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/html' and not html_body:
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            content_type = email_message.get_content_type()
            payload = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            if content_type == 'text/html':
                html_body = payload
                text_body = payload  # Fallback
            else:
                text_body = payload

        return text_body, html_body

    def _parse_email_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string"""
        try:
            import email.utils
            parsed = email.utils.parsedate_to_datetime(date_str)
            return parsed
        except:
            return None

    def _guess_folder_type(self, folder_name: str) -> str:
        """Guess folder type from name"""
        name_lower = folder_name.lower()
        if 'inbox' in name_lower:
            return 'inbox'
        elif 'sent' in name_lower:
            return 'sent'
        elif 'draft' in name_lower:
            return 'drafts'
        elif 'trash' in name_lower or 'deleted' in name_lower:
            return 'trash'
        elif 'spam' in name_lower or 'junk' in name_lower:
            return 'spam'
        else:
            return 'other'
