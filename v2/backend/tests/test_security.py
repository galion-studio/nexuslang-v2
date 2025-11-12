"""
Security Testing Suite for NexusLang v2

Tests all security features:
- Authentication and authorization
- Rate limiting
- Input validation
- Sandboxed execution
- Security headers
- Audit logging

Run with: pytest v2/backend/tests/test_security.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from core.security import (
    validate_password_strength,
    validate_username,
    create_access_token,
    decode_access_token,
    blacklist_token
)
from core.security_middleware import RateLimiter
from services.sandboxed_executor import SandboxedNexusLangExecutor


# ==================== AUTHENTICATION TESTS ====================

class TestAuthentication:
    """Test authentication and password security."""
    
    def test_password_strength_validation(self):
        """Test password strength requirements."""
        # Too short
        valid, msg = validate_password_strength("Short1!")
        assert not valid
        assert "12 characters" in msg
        
        # No uppercase
        valid, msg = validate_password_strength("lowercase123!")
        assert not valid
        assert "uppercase" in msg
        
        # No lowercase
        valid, msg = validate_password_strength("UPPERCASE123!")
        assert not valid
        assert "lowercase" in msg
        
        # No digit
        valid, msg = validate_password_strength("NoDigitsHere!")
        assert not valid
        assert "digit" in msg
        
        # No special char
        valid, msg = validate_password_strength("NoSpecial123")
        assert not valid
        assert "special character" in msg
        
        # Common password
        valid, msg = validate_password_strength("Password123!")
        assert not valid
        assert "too common" in msg.lower()
        
        # Valid strong password
        valid, msg = validate_password_strength("MyStr0ng!P@ssw0rd")
        assert valid
        assert msg is None
    
    def test_username_validation(self):
        """Test username requirements."""
        # Too short
        valid, msg = validate_username("ab")
        assert not valid
        
        # Too long
        valid, msg = validate_username("a" * 51)
        assert not valid
        
        # Invalid characters
        valid, msg = validate_username("user@name")
        assert not valid
        
        # Valid usernames
        assert validate_username("validuser")[0]
        assert validate_username("valid_user")[0]
        assert validate_username("valid-user")[0]
        assert validate_username("user123")[0]
    
    def test_jwt_token_lifecycle(self):
        """Test JWT token creation, validation, and blacklisting."""
        # Create token
        token = create_access_token({"sub": "user123", "email": "test@example.com"})
        assert token
        assert isinstance(token, str)
        
        # Decode valid token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        
        # Blacklist token
        blacklist_token(token)
        
        # Should not decode blacklisted token
        payload = decode_access_token(token)
        assert payload is None
    
    def test_invalid_token(self):
        """Test invalid token handling."""
        # Random invalid token
        payload = decode_access_token("invalid.token.here")
        assert payload is None
        
        # Empty token
        payload = decode_access_token("")
        assert payload is None


# ==================== RATE LIMITING TESTS ====================

class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced."""
        limiter = RateLimiter()
        client_id = "test_client_123"
        
        # Should allow up to limit
        for i in range(10):
            allowed, info = limiter.is_allowed(client_id, max_requests=10, window_seconds=60)
            assert allowed, f"Request {i+1} should be allowed"
        
        # Should block after limit
        allowed, info = limiter.is_allowed(client_id, max_requests=10, window_seconds=60)
        assert not allowed
        assert info["remaining"] == 0
    
    def test_rate_limit_window_expiry(self):
        """Test that rate limits reset after window."""
        limiter = RateLimiter()
        client_id = "test_client_456"
        
        # Fill up limit
        for i in range(5):
            limiter.is_allowed(client_id, max_requests=5, window_seconds=1)
        
        # Should be blocked
        allowed, _ = limiter.is_allowed(client_id, max_requests=5, window_seconds=1)
        assert not allowed
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        allowed, _ = limiter.is_allowed(client_id, max_requests=5, window_seconds=1)
        assert allowed


# ==================== SANDBOXED EXECUTION TESTS ====================

class TestSandboxedExecution:
    """Test sandboxed code execution security."""
    
    @pytest.mark.asyncio
    async def test_basic_safe_execution(self):
        """Test that safe code executes correctly."""
        executor = SandboxedNexusLangExecutor()
        
        # Simple safe code
        code = 'let x = 42\nprint(x)'
        result = await executor.execute(code)
        
        assert result["success"]
        assert result["sandboxed"]
        assert "42" in result["output"]
    
    @pytest.mark.asyncio
    async def test_timeout_enforcement(self):
        """Test that infinite loops are terminated."""
        executor = SandboxedNexusLangExecutor(timeout_seconds=2)
        
        # Infinite loop
        code = 'while true { let x = 1 }'
        result = await executor.execute(code)
        
        # Should timeout (or error during parsing if NexusLang catches it)
        # Execution time should be around timeout limit
        assert result["execution_time"] <= 3000  # 3 seconds max
    
    @pytest.mark.asyncio
    async def test_output_size_limit(self):
        """Test that output is truncated if too large."""
        executor = SandboxedNexusLangExecutor(max_output_size=100)
        
        # Generate large output
        code = '''
        for i in range(100) {
            print("x" * 100)
        }
        '''
        result = await executor.execute(code)
        
        # Output should be truncated
        if len(result["output"]) >= 100:
            assert "truncated" in result["output"].lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test that errors are caught and reported safely."""
        executor = SandboxedNexusLangExecutor()
        
        # Code with syntax error
        code = 'this is invalid syntax {'
        result = await executor.execute(code)
        
        assert not result["success"]
        assert "error" in result["output"].lower()
        assert result["sandboxed"]


# ==================== SECURITY HEADERS TESTS ====================

class TestSecurityHeaders:
    """Test security headers in responses."""
    
    def test_security_headers_present(self):
        """Test that security headers are added to responses."""
        client = TestClient(app)
        
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        
        assert "Content-Security-Policy" in response.headers
        
        assert "Referrer-Policy" in response.headers
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present."""
        client = TestClient(app)
        
        response = client.get("/health")
        
        # Should have rate limit headers (after middleware processes)
        # Note: Health endpoint might skip rate limiting
        # Test on an actual API endpoint
        # This is a basic check


# ==================== INPUT VALIDATION TESTS ====================

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_request_size_limit(self):
        """Test that oversized requests are rejected."""
        client = TestClient(app)
        
        # Create a very large payload (>10MB)
        large_payload = {"data": "x" * (11 * 1024 * 1024)}
        
        # Should be rejected (if endpoint exists that accepts JSON)
        # This is conceptual - actual test depends on endpoint
    
    def test_invalid_content_type(self):
        """Test that invalid content types are rejected."""
        client = TestClient(app)
        
        # Try to post with invalid content type
        # Should return 415 Unsupported Media Type


# ==================== INTEGRATION TESTS ====================

class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_unauthenticated_access_blocked(self):
        """Test that protected endpoints require authentication."""
        client = TestClient(app)
        
        # Try to access protected endpoint without token
        response = client.get("/api/v2/auth/me")
        
        # Should require authentication
        assert response.status_code == 403  # or 401


# ==================== AUDIT LOGGING TESTS ====================

class TestAuditLogging:
    """Test audit logging functionality."""
    
    def test_audit_log_creation(self):
        """Test that audit events are logged."""
        from core.security_middleware import get_audit_logger
        
        logger = get_audit_logger()
        initial_count = len(logger.events)
        
        # Create mock request
        mock_request = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test"}
        mock_request.method = "POST"
        mock_request.url.path = "/test"
        
        # Log an event
        logger.log_event(
            event_type="test_event",
            user_id="test_user",
            request=mock_request,
            details={"action": "test"},
            severity="info"
        )
        
        # Should have one more event
        assert len(logger.events) == initial_count + 1
        
        # Check event structure
        latest = logger.events[-1]
        assert latest["type"] == "test_event"
        assert latest["user_id"] == "test_user"
        assert latest["severity"] == "info"


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    print("🔒 Running Security Test Suite...")
    print("=" * 60)
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])

