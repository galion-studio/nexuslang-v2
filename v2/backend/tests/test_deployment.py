"""
Deployment Tests for NexusLang v2
==================================

Automated pytest tests for deployment validation.

Run with:
    pytest tests/test_deployment.py -v
    pytest tests/test_deployment.py --cov
"""

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid

from core.config import settings
from core.database import get_db
from core.redis_client import get_redis


class TestBasicDeployment:
    """Test basic deployment requirements."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health endpoint responds correctly."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'healthy'
            assert 'version' in data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            
            assert response.status_code == 200
            data = response.json()
            assert 'message' in data
            assert 'docs' in data
    
    @pytest.mark.asyncio
    async def test_api_docs_accessible(self):
        """Test API documentation is accessible."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/docs")
            
            assert response.status_code == 200
            assert 'swagger' in response.text.lower()


class TestDatabaseConnectivity:
    """Test database connectivity and schema."""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection works."""
        async for db in get_db():
            result = await db.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
            break
    
    @pytest.mark.asyncio
    async def test_required_tables_exist(self):
        """Test all required tables exist."""
        required_tables = [
            'users',
            'sessions',
            'api_keys',
            'projects',
            'files'
        ]
        
        async for db in get_db():
            for table in required_tables:
                result = await db.execute(
                    text(f"""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = :table
                        )
                    """),
                    {'table': table}
                )
                exists = result.scalar()
                assert exists, f"Table {table} does not exist"
            break
    
    @pytest.mark.asyncio
    async def test_analytics_schema_exists(self):
        """Test analytics schema is created."""
        async for db in get_db():
            result = await db.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.schemata 
                        WHERE schema_name = 'analytics'
                    )
                """)
            )
            exists = result.scalar()
            assert exists, "Analytics schema does not exist"
            break
    
    @pytest.mark.asyncio
    async def test_pgvector_extension(self):
        """Test pgvector extension is installed."""
        async for db in get_db():
            result = await db.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_extension 
                        WHERE extname = 'vector'
                    )
                """)
            )
            exists = result.scalar()
            # pgvector is optional, so just warn if missing
            if not exists:
                pytest.skip("pgvector extension not installed (optional)")
            break


class TestRedisConnectivity:
    """Test Redis connectivity and operations."""
    
    @pytest.mark.asyncio
    async def test_redis_ping(self):
        """Test Redis ping."""
        redis = await get_redis()
        
        if not redis.is_connected:
            pytest.skip("Redis not connected (using fallback mode)")
        
        pong = await redis.client.ping()
        assert pong == True
    
    @pytest.mark.asyncio
    async def test_redis_set_get(self):
        """Test Redis set and get operations."""
        redis = await get_redis()
        
        if not redis.is_connected:
            pytest.skip("Redis not connected (using fallback mode)")
        
        test_key = f"test_{uuid.uuid4()}"
        test_value = "deployment_test"
        
        # Set
        await redis.client.set(test_key, test_value, ex=10)
        
        # Get
        value = await redis.client.get(test_key)
        assert value == test_value
        
        # Cleanup
        await redis.client.delete(test_key)


class TestAuthenticationFlow:
    """Test complete authentication flow."""
    
    @pytest.mark.asyncio
    async def test_user_registration(self):
        """Test user can register."""
        test_user = {
            'username': f'test_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPass123!'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v2/auth/register",
                json=test_user
            )
            
            assert response.status_code in [200, 201], f"Registration failed: {response.text}"
            data = response.json()
            assert 'id' in data or 'user' in data
    
    @pytest.mark.asyncio
    async def test_login_returns_token(self):
        """Test login returns valid JWT token."""
        # First register a user
        test_user = {
            'username': f'test_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPass123!'
        }
        
        async with httpx.AsyncClient() as client:
            # Register
            await client.post(
                "http://localhost:8000/api/v2/auth/register",
                json=test_user
            )
            
            # Login
            response = await client.post(
                "http://localhost:8000/api/v2/auth/login",
                json={
                    'username': test_user['username'],
                    'password': test_user['password']
                }
            )
            
            assert response.status_code == 200, f"Login failed: {response.text}"
            data = response.json()
            assert 'access_token' in data
            assert len(data['access_token']) > 20  # JWT token should be long


class TestAnalyticsSystem:
    """Test analytics system is working."""
    
    @pytest.mark.asyncio
    async def test_analytics_tables_exist(self):
        """Test analytics tables are created."""
        required_tables = [
            'events',
            'user_sessions',
            'ai_usage',
            'api_performance',
            'errors'
        ]
        
        async for db in get_db():
            for table in required_tables:
                result = await db.execute(
                    text(f"""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_schema = 'analytics'
                            AND table_name = :table
                        )
                    """),
                    {'table': table}
                )
                exists = result.scalar()
                assert exists, f"Analytics table {table} does not exist"
            break
    
    @pytest.mark.asyncio
    async def test_can_insert_event(self):
        """Test can insert analytics event."""
        async for db in get_db():
            await db.execute(
                text("""
                    INSERT INTO analytics.events (
                        event_type, category, service, data
                    ) VALUES (
                        'test_event', 'system', 'test', '{}'::jsonb
                    )
                """)
            )
            await db.commit()
            
            # Verify inserted
            result = await db.execute(
                text("""
                    SELECT COUNT(*) FROM analytics.events 
                    WHERE event_type = 'test_event'
                """)
            )
            count = result.scalar()
            assert count > 0
            break


class TestCriticalEndpoints:
    """Test critical API endpoints are accessible."""
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/metrics")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_detailed_health(self):
        """Test detailed health check."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health/detailed")
            assert response.status_code == 200
            
            data = response.json()
            assert 'overall_status' in data
            assert 'checks' in data


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])

