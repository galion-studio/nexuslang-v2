#!/usr/bin/env python3
"""
Seed script for mail providers
Creates supported email providers configuration
"""

import asyncio
from ..core.database import get_db
from ..models.mail import MailProvider

# Supported mail providers configuration
MAIL_PROVIDERS = [
    {
        "name": "gmail",
        "display_name": "Gmail",
        "client_id": "your-gmail-client-id",  # To be configured
        "client_secret": "your-gmail-client-secret",  # To be configured
        "auth_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify",
        "imap_host": "imap.gmail.com",
        "imap_port": "993",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "outlook",
        "display_name": "Outlook",
        "client_id": "your-outlook-client-id",  # To be configured
        "client_secret": "your-outlook-client-secret",  # To be configured
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "scope": "https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Send",
        "imap_host": "outlook.office365.com",
        "imap_port": "993",
        "smtp_host": "smtp-mail.outlook.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "yahoo",
        "display_name": "Yahoo Mail",
        "client_id": "your-yahoo-client-id",  # To be configured
        "client_secret": "your-yahoo-client-secret",  # To be configured
        "auth_url": "https://api.login.yahoo.com/oauth2/request_auth",
        "token_url": "https://api.login.yahoo.com/oauth2/get_token",
        "scope": "mail-r mail-w",
        "imap_host": "imap.mail.yahoo.com",
        "imap_port": "993",
        "smtp_host": "smtp.mail.yahoo.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "icloud",
        "display_name": "iCloud Mail",
        "client_id": "your-icloud-client-id",  # To be configured
        "client_secret": "your-icloud-client-secret",  # To be configured
        "auth_url": "https://appleid.apple.com/auth/authorize",
        "token_url": "https://appleid.apple.com/auth/token",
        "scope": "name email",
        "imap_host": "imap.mail.me.com",
        "imap_port": "993",
        "smtp_host": "smtp.mail.me.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "fastmail",
        "display_name": "Fastmail",
        "client_id": None,  # IMAP/SMTP only
        "client_secret": None,
        "auth_url": None,
        "token_url": None,
        "scope": None,
        "imap_host": "imap.fastmail.com",
        "imap_port": "993",
        "smtp_host": "smtp.fastmail.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "protonmail",
        "display_name": "ProtonMail",
        "client_id": None,  # IMAP/SMTP only
        "client_secret": None,
        "auth_url": None,
        "token_url": None,
        "scope": None,
        "imap_host": "127.0.0.1",  # Requires Bridge
        "imap_port": "1143",
        "smtp_host": "127.0.0.1",  # Requires Bridge
        "smtp_port": "1025",
        "is_active": True
    },
    {
        "name": "zoho",
        "display_name": "Zoho Mail",
        "client_id": "your-zoho-client-id",  # To be configured
        "client_secret": "your-zoho-client-secret",  # To be configured
        "auth_url": "https://accounts.zoho.com/oauth/v2/auth",
        "token_url": "https://accounts.zoho.com/oauth/v2/token",
        "scope": "ZohoMail.accounts.READ ZohoMail.messages.ALL",
        "imap_host": "imap.zoho.com",
        "imap_port": "993",
        "smtp_host": "smtp.zoho.com",
        "smtp_port": "587",
        "is_active": True
    },
    {
        "name": "custom",
        "display_name": "Custom IMAP/SMTP",
        "client_id": None,
        "client_secret": None,
        "auth_url": None,
        "token_url": None,
        "scope": None,
        "imap_host": None,
        "imap_port": "993",
        "smtp_host": None,
        "smtp_port": "587",
        "is_active": True
    }
]


async def seed_mail_providers():
    """Seed mail providers into database"""
    async for db in get_db():
        try:
            for provider_data in MAIL_PROVIDERS:
                # Check if provider already exists
                existing = db.query(MailProvider).filter(MailProvider.name == provider_data["name"]).first()

                if existing:
                    # Update existing provider
                    for key, value in provider_data.items():
                        setattr(existing, key, value)
                    print(f"Updated mail provider: {provider_data['name']}")
                else:
                    # Create new provider
                    provider = MailProvider(**provider_data)
                    db.add(provider)
                    print(f"Created mail provider: {provider_data['name']}")

            await db.commit()
            print("Mail providers seeded successfully!")

        except Exception as e:
            print(f"Error seeding mail providers: {e}")
            await db.rollback()
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(seed_mail_providers())
