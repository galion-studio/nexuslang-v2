"""
Comprehensive Health Check System for NexusLang v2
===================================================

Multi-level health validation for deployment verification.

Features:
- Database connectivity and schema validation
- Redis connectivity and performance
- AI provider connectivity testing
- Disk space monitoring
- Memory usage tracking
- Import validation
- Extension verification
"""

import asyncio
import psutil
import shutil
from typing import Dict, Any, List
from datetime import datetime, timezone
from pathlib import Path
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.redis_client import get_redis
from core.config import settings


class HealthCheckSystem:
    """
    Comprehensive health check system for platform validation.
    """
    
    def __init__(self):
        """Initialize health check system."""
        self.checks = {
            'database': self.check_database,
            'redis': self.check_redis,
            'ai_provider': self.check_ai_provider,
            'disk_space': self.check_disk_space,
            'memory': self.check_memory,
            'imports': self.check_imports,
            'extensions': self.check_database_extensions,
            'tables': self.check_database_tables
        }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Dict with health check results for all components
        """
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Run all checks
        for check_name, check_func in self.checks.items():
            try:
                check_result = await check_func()
                results['checks'][check_name] = check_result
                
                # Update overall status
                if check_result['status'] == 'unhealthy':
                    results['overall_status'] = 'unhealthy'
                elif check_result['status'] == 'degraded' and results['overall_status'] == 'healthy':
                    results['overall_status'] = 'degraded'
                    
            except Exception as e:
                results['checks'][check_name] = {
                    'status': 'unhealthy',
                    'message': f'Health check failed: {str(e)}',
                    'error': str(e)
                }
                results['overall_status'] = 'unhealthy'
        
        return results
    
    async def check_database(self) -> Dict[str, Any]:
        """
        Check PostgreSQL database connectivity and performance.
        
        Returns:
            Health check result for database
        """
        try:
            async for db in get_db():
                # Test basic connectivity with a simple query
                start_time = asyncio.get_event_loop().time()
                result = await db.execute(text("SELECT 1"))
                query_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                # Test database info
                result = await db.execute(text("SELECT version()"))
                version = result.scalar()
                
                # Test connection pool
                result = await db.execute(
                    text("SELECT count(*) FROM pg_stat_activity WHERE datname = :dbname"),
                    {'dbname': settings.POSTGRES_DB}
                )
                connections = result.scalar()
                
                # Determine status based on query time
                if query_time < 10:
                    status = 'healthy'
                elif query_time < 100:
                    status = 'degraded'
                else:
                    status = 'unhealthy'
                
                return {
                    'status': status,
                    'message': 'Database connection successful',
                    'details': {
                        'version': version.split(',')[0] if version else 'unknown',
                        'query_time_ms': round(query_time, 2),
                        'active_connections': connections,
                        'database': settings.POSTGRES_DB,
                        'host': self._get_db_host()
                    }
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """
        Check Redis connectivity and performance.
        
        Returns:
            Health check result for Redis
        """
        try:
            redis = await get_redis()
            
            if not redis.is_connected:
                return {
                    'status': 'degraded',
                    'message': 'Redis not connected (using in-memory fallback)',
                    'details': {
                        'fallback_mode': True
                    }
                }
            
            # Test ping
            start_time = asyncio.get_event_loop().time()
            pong = await redis.client.ping()
            ping_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Test set/get
            test_key = f"health_check_{uuid.uuid4()}"
            await redis.client.set(test_key, "test", ex=10)
            value = await redis.client.get(test_key)
            await redis.client.delete(test_key)
            
            # Get Redis info
            info = await redis.client.info()
            
            # Determine status
            if ping_time < 5:
                status = 'healthy'
            elif ping_time < 20:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'message': 'Redis connection successful',
                'details': {
                    'ping_time_ms': round(ping_time, 2),
                    'version': info.get('redis_version', 'unknown'),
                    'used_memory_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
                    'connected_clients': info.get('connected_clients', 0)
                }
            }
            
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Redis check failed (non-critical): {str(e)}',
                'details': {
                    'fallback_mode': True
                }
            }
    
    async def check_ai_provider(self) -> Dict[str, Any]:
        """
        Check AI provider connectivity (OpenRouter).
        
        Returns:
            Health check result for AI provider
        """
        try:
            import httpx
            
            if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == 'test':
                return {
                    'status': 'degraded',
                    'message': 'OpenRouter API key not configured',
                    'details': {
                        'configured': False
                    }
                }
            
            # Test API connectivity with a simple request
            start_time = asyncio.get_event_loop().time()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.OPENROUTER_BASE_URL}/models",
                    headers={
                        'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}'
                    },
                    timeout=5.0
                )
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                model_count = len(data.get('data', []))
                
                return {
                    'status': 'healthy',
                    'message': 'AI provider accessible',
                    'details': {
                        'provider': 'openrouter',
                        'response_time_ms': round(response_time, 2),
                        'available_models': model_count,
                        'configured': True
                    }
                }
            else:
                return {
                    'status': 'degraded',
                    'message': f'AI provider returned status {response.status_code}',
                    'details': {
                        'status_code': response.status_code
                    }
                }
                
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'AI provider check failed (non-critical): {str(e)}',
                'details': {
                    'error': str(e)
                }
            }
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space.
        
        Returns:
            Health check result for disk space
        """
        try:
            # Check /workspace directory (RunPod network volume)
            workspace_path = Path('/workspace')
            if workspace_path.exists():
                usage = shutil.disk_usage(workspace_path)
                percent_used = (usage.used / usage.total) * 100
                
                # Determine status based on usage
                if percent_used < 80:
                    status = 'healthy'
                elif percent_used < 90:
                    status = 'degraded'
                else:
                    status = 'unhealthy'
                
                return {
                    'status': status,
                    'message': f'Disk usage: {percent_used:.1f}%',
                    'details': {
                        'total_gb': round(usage.total / 1024 / 1024 / 1024, 2),
                        'used_gb': round(usage.used / 1024 / 1024 / 1024, 2),
                        'free_gb': round(usage.free / 1024 / 1024 / 1024, 2),
                        'percent_used': round(percent_used, 2)
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'message': 'Workspace directory not found (using container storage)',
                    'details': {}
                }
                
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Disk space check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage.
        
        Returns:
            Health check result for memory
        """
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            # Determine status
            if percent_used < 80:
                status = 'healthy'
            elif percent_used < 90:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'message': f'Memory usage: {percent_used:.1f}%',
                'details': {
                    'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                    'used_gb': round(memory.used / 1024 / 1024 / 1024, 2),
                    'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                    'percent_used': percent_used
                }
            }
            
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Memory check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_imports(self) -> Dict[str, Any]:
        """
        Validate critical Python imports.
        
        Returns:
            Health check result for imports
        """
        try:
            critical_imports = [
                'fastapi',
                'uvicorn',
                'sqlalchemy',
                'redis',
                'pydantic',
                'httpx'
            ]
            
            failed_imports = []
            
            for module_name in critical_imports:
                try:
                    __import__(module_name)
                except ImportError:
                    failed_imports.append(module_name)
            
            if not failed_imports:
                return {
                    'status': 'healthy',
                    'message': 'All critical imports available',
                    'details': {
                        'checked': critical_imports,
                        'failed': []
                    }
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'Missing imports: {", ".join(failed_imports)}',
                    'details': {
                        'checked': critical_imports,
                        'failed': failed_imports
                    }
                }
                
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Import check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_database_extensions(self) -> Dict[str, Any]:
        """
        Check if required PostgreSQL extensions are installed.
        
        Returns:
            Health check result for database extensions
        """
        try:
            async for db in get_db():
                required_extensions = ['uuid-ossp', 'vector']
                installed = []
                missing = []
                
                for ext in required_extensions:
                    result = await db.execute(
                        text("""
                            SELECT EXISTS(
                                SELECT 1 FROM pg_extension WHERE extname = :ext
                            )
                        """),
                        {'ext': ext}
                    )
                    if result.scalar():
                        installed.append(ext)
                    else:
                        missing.append(ext)
                
                if not missing:
                    return {
                        'status': 'healthy',
                        'message': 'All required extensions installed',
                        'details': {
                            'required': required_extensions,
                            'installed': installed,
                            'missing': []
                        }
                    }
                else:
                    # Vector is critical for Grokopedia, uuid-ossp is nice to have
                    status = 'degraded' if 'vector' not in missing else 'unhealthy'
                    
                    return {
                        'status': status,
                        'message': f'Missing extensions: {", ".join(missing)}',
                        'details': {
                            'required': required_extensions,
                            'installed': installed,
                            'missing': missing
                        }
                    }
                    
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Extension check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_database_tables(self) -> Dict[str, Any]:
        """
        Check if critical database tables exist.
        
        Returns:
            Health check result for database tables
        """
        try:
            async for db in get_db():
                critical_tables = [
                    'users',
                    'sessions',
                    'projects',
                    'files',
                    'analytics.events',
                    'analytics.ai_usage'
                ]
                
                existing = []
                missing = []
                
                for table in critical_tables:
                    # Split schema and table if schema prefix exists
                    if '.' in table:
                        schema, table_name = table.split('.')
                        query = text("""
                            SELECT EXISTS(
                                SELECT 1 FROM information_schema.tables 
                                WHERE table_schema = :schema 
                                AND table_name = :table
                            )
                        """)
                        params = {'schema': schema, 'table': table_name}
                    else:
                        query = text("""
                            SELECT EXISTS(
                                SELECT 1 FROM information_schema.tables 
                                WHERE table_name = :table
                            )
                        """)
                        params = {'table': table}
                    
                    result = await db.execute(query, params)
                    if result.scalar():
                        existing.append(table)
                    else:
                        missing.append(table)
                
                if not missing:
                    return {
                        'status': 'healthy',
                        'message': 'All critical tables exist',
                        'details': {
                            'checked': critical_tables,
                            'existing': existing,
                            'missing': []
                        }
                    }
                else:
                    return {
                        'status': 'degraded',
                        'message': f'Missing tables: {", ".join(missing)}',
                        'details': {
                            'checked': critical_tables,
                            'existing': existing,
                            'missing': missing
                        }
                    }
                    
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Table check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """
        Check Redis connectivity and performance.
        
        Returns:
            Health check result for Redis
        """
        try:
            redis = await get_redis()
            
            if not redis.is_connected:
                return {
                    'status': 'degraded',
                    'message': 'Redis not connected (using in-memory fallback)',
                    'details': {
                        'connected': False,
                        'fallback_mode': True
                    }
                }
            
            # Test ping
            start_time = asyncio.get_event_loop().time()
            pong = await redis.client.ping()
            ping_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Test operations
            test_key = f"health_{uuid.uuid4()}"
            await redis.client.set(test_key, "test", ex=5)
            value = await redis.client.get(test_key)
            await redis.client.delete(test_key)
            
            # Get info
            info = await redis.client.info()
            
            # Determine status
            if ping_time < 5:
                status = 'healthy'
            elif ping_time < 20:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'message': 'Redis connection successful',
                'details': {
                    'connected': True,
                    'ping_time_ms': round(ping_time, 2),
                    'version': info.get('redis_version', 'unknown'),
                    'uptime_days': info.get('uptime_in_days', 0)
                }
            }
            
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'Redis check failed (non-critical): {str(e)}',
                'details': {
                    'connected': False,
                    'fallback_mode': True
                }
            }
    
    async def check_ai_provider(self) -> Dict[str, Any]:
        """
        Check AI provider (OpenRouter) connectivity.
        
        Returns:
            Health check result for AI provider
        """
        try:
            import httpx
            
            if not settings.OPENROUTER_API_KEY or 'test' in settings.OPENROUTER_API_KEY.lower():
                return {
                    'status': 'degraded',
                    'message': 'OpenRouter API key not configured',
                    'details': {
                        'configured': False,
                        'provider': 'openrouter'
                    }
                }
            
            # Quick connectivity test
            start_time = asyncio.get_event_loop().time()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.OPENROUTER_BASE_URL}/models",
                    headers={'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}'},
                    timeout=5.0
                )
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'AI provider accessible',
                    'details': {
                        'provider': 'openrouter',
                        'response_time_ms': round(response_time, 2),
                        'configured': True
                    }
                }
            else:
                return {
                    'status': 'degraded',
                    'message': f'AI provider returned {response.status_code}',
                    'details': {
                        'status_code': response.status_code
                    }
                }
                
        except Exception as e:
            return {
                'status': 'degraded',
                'message': f'AI provider check failed: {str(e)}',
                'error': str(e)
            }
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability."""
        try:
            workspace = Path('/workspace')
            if workspace.exists():
                usage = shutil.disk_usage(workspace)
                percent_used = (usage.used / usage.total) * 100
                
                if percent_used < 80:
                    status = 'healthy'
                elif percent_used < 90:
                    status = 'degraded'
                else:
                    status = 'unhealthy'
                
                return {
                    'status': status,
                    'message': f'{percent_used:.1f}% disk used',
                    'details': {
                        'total_gb': round(usage.total / 1024**3, 2),
                        'free_gb': round(usage.free / 1024**3, 2),
                        'percent_used': round(percent_used, 2)
                    }
                }
            else:
                return {'status': 'healthy', 'message': 'Container storage', 'details': {}}
                
        except Exception as e:
            return {'status': 'degraded', 'message': str(e), 'error': str(e)}
    
    async def check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            mem = psutil.virtual_memory()
            
            if mem.percent < 80:
                status = 'healthy'
            elif mem.percent < 90:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            return {
                'status': status,
                'message': f'{mem.percent:.1f}% memory used',
                'details': {
                    'total_gb': round(mem.total / 1024**3, 2),
                    'available_gb': round(mem.available / 1024**3, 2),
                    'percent_used': mem.percent
                }
            }
            
        except Exception as e:
            return {'status': 'degraded', 'message': str(e), 'error': str(e)}
    
    async def check_imports(self) -> Dict[str, Any]:
        """Validate critical imports."""
        critical = ['fastapi', 'uvicorn', 'sqlalchemy', 'redis', 'pydantic', 'httpx']
        failed = []
        
        for mod in critical:
            try:
                __import__(mod)
            except ImportError:
                failed.append(mod)
        
        if not failed:
            return {'status': 'healthy', 'message': 'All imports OK', 'details': {'checked': critical}}
        else:
            return {'status': 'unhealthy', 'message': f'Missing: {", ".join(failed)}', 'details': {'failed': failed}}
    
    def _get_db_host(self) -> str:
        """Extract database host from DATABASE_URL."""
        url = settings.DATABASE_URL
        if '@' in url:
            after_at = url.split('@')[1]
            if '/' in after_at:
                host_port = after_at.split('/')[0]
                if ':' in host_port:
                    return host_port.split(':')[0]
                return host_port
        return 'localhost'


# Global health check system instance
_health_check_system: Optional[HealthCheckSystem] = None


def get_health_check_system() -> HealthCheckSystem:
    """
    Get or create global health check system instance.
    
    Returns:
        HealthCheckSystem instance
    """
    global _health_check_system
    
    if _health_check_system is None:
        _health_check_system = HealthCheckSystem()
    
    return _health_check_system

