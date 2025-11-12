"""
Email Service - Zoho Mail Integration
Handles transactional emails for the platform
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import os
from jinja2 import Template

# Zoho Mail SMTP Configuration
SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "info@galion.studio")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = "info@galion.studio"
SMTP_FROM_NAME = "Galion Studio"


class EmailService:
    """Service for sending transactional emails"""
    
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email via Zoho Mail SMTP.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback
            
        Returns:
            True if sent successfully
        """
        if not self.smtp_password:
            print(f"⚠️  Email not sent - SMTP not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to NexusLang v2! 🚀"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                <h1 style="color: white; margin: 0;">Welcome to NexusLang v2!</h1>
            </div>
            <div style="padding: 40px; background: #f9fafb;">
                <p style="font-size: 16px; color: #333;">Hi {username},</p>
                <p style="font-size: 16px; color: #333;">
                    Welcome to the future of AI development! You now have access to the world's first AI-native programming language.
                </p>
                <h3 style="color: #667eea;">What you can do:</h3>
                <ul style="font-size: 14px; color: #666;">
                    <li>Execute NexusLang code with 10x faster binary compilation</li>
                    <li>Chat with AI assistants (Claude, GPT-4, and more)</li>
                    <li>Generate images, videos, and content</li>
                    <li>Access Grokopedia knowledge base</li>
                    <li>Use voice-to-voice AI features</li>
                </ul>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://developer.galion.app/ide" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">Start Coding</a>
                </div>
                <p style="font-size: 14px; color: #999;">
                    You have <strong>100 free credits</strong> to get started. No credit card required.
                </p>
            </div>
            <div style="padding: 20px; text-align: center; font-size: 12px; color: #999;">
                <p>Galion Studio | Built with First Principles</p>
                <p>Questions? Reply to this email or visit our <a href="https://developer.galion.app/developers">documentation</a></p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to NexusLang v2, {username}!
        
        You now have access to the world's first AI-native programming language.
        
        Get started: https://developer.galion.app/ide
        
        You have 100 free credits to explore all features.
        
        - Galion Studio Team
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"https://developer.galion.app/auth/reset-password?token={reset_token}"
        
        subject = "Reset Your Password - NexusLang v2"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="padding: 40px; background: #f9fafb;">
                <h2 style="color: #333;">Password Reset Request</h2>
                <p style="font-size: 16px; color: #666;">
                    Click the button below to reset your password. This link expires in 1 hour.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">Reset Password</a>
                </div>
                <p style="font-size: 14px; color: #999;">
                    If you didn't request this, you can safely ignore this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_body)
    
    def send_admin_notification(
        self,
        subject: str,
        message: str,
        notify_all: bool = False
    ) -> bool:
        """Send notification to admin(s)"""
        from .admin_config import ADMIN_EMAILS, PRIMARY_ADMIN
        
        recipients = ADMIN_EMAILS if notify_all else [PRIMARY_ADMIN.email]
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Admin Notification</h2>
            <p><strong>Subject:</strong> {subject}</p>
            <p>{message}</p>
            <p style="font-size: 12px; color: #999;">This is an automated notification from NexusLang v2</p>
        </body>
        </html>
        """
        
        success = True
        for email in recipients:
            if not self.send_email(email, f"[Admin] {subject}", html_body):
                success = False
        
        return success


# Global email service instance
_email_service = None

def get_email_service() -> EmailService:
    """Get email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

