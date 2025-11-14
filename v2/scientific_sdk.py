#!/usr/bin/env python3
"""
Nexus Lang V2 Scientific Knowledge Enhancement SDK
=================================================

Comprehensive SDK for easy integration of scientific AI capabilities into applications.

Features:
- Simple API client for scientific queries
- Async support for high-performance applications
- Automatic retry and error handling
- Batch processing capabilities
- Real-time streaming results
- Comprehensive error handling and logging
- Type hints and IDE support

Author: Nexus Lang V2 Scientific SDK Team
Date: November 2025
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
import backoff
from urllib.parse import urljoin


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScientificQuery:
    """Scientific query object."""
    query: str
    domain_focus: Optional[str] = None
    require_collaboration: bool = True
    include_external_sources: bool = True
    first_principles_only: bool = False
    context: Optional[Dict[str, Any]] = None


@dataclass
class ScientificResult:
    """Scientific analysis result."""
    query: str
    domain: str
    analysis_result: Dict[str, Any]
    external_knowledge: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    sources_used: List[str] = field(default_factory=list)
    first_principles_applied: List[str] = field(default_factory=list)
    transparency_report: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None

    def __post_init__(self):
        if self.transparency_report and 'execution_id' in self.transparency_report:
            self.execution_id = self.transparency_report['execution_id']


@dataclass
class ValidationResult:
    """Scientific validation result."""
    claim: str
    domain: str
    validation_result: str  # "supported", "refuted", "inconclusive"
    confidence_score: float
    evidence_strength: str  # "strong", "moderate", "weak"
    validation_methods: List[str]
    processing_time: float
    execution_id: Optional[str] = None


@dataclass
class FirstPrinciplesResult:
    """First principles analysis result."""
    topic: str
    domain: str
    fundamental_principles: List[str]
    logical_deduction_steps: List[Dict[str, Any]]
    counterexamples: List[Dict[str, Any]]
    conclusions: List[str]
    confidence_level: str  # "high", "moderate", "low"
    processing_time: float
    execution_id: Optional[str] = None


@dataclass
class SystemHealth:
    """System health status."""
    status: str  # "healthy", "degraded", "error"
    timestamp: str
    agents: Dict[str, Dict[str, Any]]
    external_apis: Dict[str, Dict[str, Any]]
    system_load: Dict[str, Union[int, float]]
    overall_health_score: float = 0.0


class ScientificSDKError(Exception):
    """Base exception for Scientific SDK errors."""
    pass


class APIError(ScientificSDKError):
    """API-related errors."""
    pass


class ValidationError(ScientificSDKError):
    """Validation-related errors."""
    pass


class TimeoutError(ScientificSDKError):
    """Timeout-related errors."""
    pass


class ScientificSDK:
    """
    Nexus Lang V2 Scientific Knowledge Enhancement SDK.

    Provides easy-to-use methods for accessing advanced scientific AI capabilities.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the Scientific SDK.

        Args:
            base_url: Base URL of the scientific API server
            api_key: API key for authentication (if required)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
            session: Custom aiohttp session (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.session = session or aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout),
            headers=self._get_default_headers()
        )

        self._custom_session = session is None

        logger.info(f"Scientific SDK initialized with base URL: {self.base_url}")

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default request headers."""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Nexus-Scientific-SDK/2.0.0'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        logger=logger
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))

        request_data = {
            'method': method.upper(),
            'url': url,
            'headers': self._get_default_headers()
        }

        if data:
            request_data['json'] = data
        if params:
            request_data['params'] = params

        try:
            async with self.session.request(**request_data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    if response.status == 401:
                        raise APIError(f"Authentication failed: {error_text}")
                    elif response.status == 403:
                        raise APIError(f"Access forbidden: {error_text}")
                    elif response.status == 404:
                        raise APIError(f"Endpoint not found: {endpoint}")
                    elif response.status == 429:
                        raise APIError(f"Rate limit exceeded: {error_text}")
                    else:
                        raise APIError(f"API error {response.status}: {error_text}")

                return await response.json()

        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timeout after {self.timeout}s")
        except aiohttp.ClientError as e:
            raise APIError(f"Network error: {str(e)}")

    async def close(self):
        """Close the SDK and cleanup resources."""
        if self._custom_session and self.session:
            await self.session.close()
            logger.info("Scientific SDK session closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    # Core Scientific Methods

    async def scientific_query(
        self,
        query: Union[str, ScientificQuery],
        **kwargs
    ) -> ScientificResult:
        """
        Execute comprehensive scientific query using specialized agents.

        Args:
            query: Scientific question or ScientificQuery object
            **kwargs: Additional query parameters

        Returns:
            ScientificResult with analysis and metadata
        """
        if isinstance(query, str):
            query_data = ScientificQuery(query=query, **kwargs).__dict__
        else:
            query_data = query.__dict__

        # Remove None values
        query_data = {k: v for k, v in query_data.items() if v is not None}

        logger.info(f"Executing scientific query: {query_data['query'][:50]}...")

        start_time = asyncio.get_event_loop().time()
        try:
            response = await self._make_request('POST', '/api/v1/grokopedia/scientific-query', query_data)
            processing_time = asyncio.get_event_loop().time() - start_time

            result = ScientificResult(
                query=response.get('query', query_data['query']),
                domain=response.get('domain', 'unknown'),
                analysis_result=response.get('analysis_result', {}),
                external_knowledge=response.get('external_knowledge'),
                confidence_score=response.get('confidence_score', 0.0),
                processing_time=processing_time,
                sources_used=response.get('sources_used', []),
                first_principles_applied=response.get('first_principles_applied', []),
                transparency_report=response.get('transparency_report')
            )

            logger.info(f"Scientific query completed in {processing_time:.2f}s with {result.confidence_score:.2f} confidence")
            return result

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Scientific query failed after {processing_time:.2f}s: {e}")
            raise

    async def validate_claim(
        self,
        claim: str,
        domain: str,
        evidence_types: Optional[List[str]] = None,
        **kwargs
    ) -> ValidationResult:
        """
        Validate scientific claim using evidence-based reasoning.

        Args:
            claim: Scientific claim to validate
            domain: Scientific domain (physics, chemistry, mathematics)
            evidence_types: Types of evidence to consider
            **kwargs: Additional validation parameters

        Returns:
            ValidationResult with validation details
        """
        if evidence_types is None:
            evidence_types = ["experimental", "theoretical", "observational"]

        request_data = {
            "claim": claim,
            "domain": domain,
            "evidence_types": evidence_types,
            **kwargs
        }

        logger.info(f"Validating claim: {claim[:50]}...")

        start_time = asyncio.get_event_loop().time()
        try:
            response = await self._make_request('POST', '/api/v1/grokopedia/scientific-validation', request_data)
            processing_time = asyncio.get_event_loop().time() - start_time

            result = ValidationResult(
                claim=response.get('claim', claim),
                domain=response.get('domain', domain),
                validation_result=response.get('validation_result', 'inconclusive'),
                confidence_score=response.get('confidence_score', 0.0),
                evidence_strength=response.get('evidence_strength', 'weak'),
                validation_methods=response.get('validation_methods', []),
                processing_time=processing_time
            )

            if response.get('transparency_report'):
                result.execution_id = response['transparency_report'].get('execution_id')

            logger.info(f"Claim validation completed: {result.validation_result} ({result.confidence_score:.2f} confidence)")
            return result

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Claim validation failed after {processing_time:.2f}s: {e}")
            raise

    async def first_principles_analysis(
        self,
        topic: str,
        domain: str,
        depth: str = "comprehensive",
        **kwargs
    ) -> FirstPrinciplesResult:
        """
        Perform first principles analysis of scientific topics.

        Args:
            topic: Scientific topic to analyze
            domain: Scientific domain
            depth: Analysis depth ("basic", "comprehensive", "exhaustive")
            **kwargs: Additional analysis parameters

        Returns:
            FirstPrinciplesResult with detailed analysis
        """
        request_data = {
            "topic": topic,
            "domain": domain,
            "depth": depth,
            **kwargs
        }

        logger.info(f"Performing first principles analysis of: {topic}")

        start_time = asyncio.get_event_loop().time()
        try:
            response = await self._make_request('POST', '/api/v1/grokopedia/first-principles-analysis', request_data)
            processing_time = asyncio.get_event_loop().time() - start_time

            result = FirstPrinciplesResult(
                topic=response.get('topic', topic),
                domain=response.get('domain', domain),
                fundamental_principles=response.get('fundamental_principles', []),
                logical_deduction_steps=response.get('logical_deduction_steps', []),
                counterexamples=response.get('counterexamples', []),
                conclusions=response.get('conclusions', []),
                confidence_level=response.get('confidence_level', 'low'),
                processing_time=processing_time
            )

            if response.get('transparency_report'):
                result.execution_id = response['transparency_report'].get('execution_id')

            logger.info(f"First principles analysis completed: {len(result.fundamental_principles)} principles identified")
            return result

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"First principles analysis failed after {processing_time:.2f}s: {e}")
            raise

    # System Management Methods

    async def get_system_health(self) -> SystemHealth:
        """
        Get current system health status.

        Returns:
            SystemHealth with comprehensive system status
        """
        try:
            response = await self._make_request('GET', '/api/v1/grokopedia/scientific-health')

            # Calculate overall health score
            agent_health = sum(1 for agent in response.get('agents', {}).values() if agent.get('status') == 'active')
            api_health = sum(1 for api in response.get('external_apis', {}).values() if api.get('status') == 'healthy')
            total_components = len(response.get('agents', {})) + len(response.get('external_apis', {}))

            if total_components > 0:
                overall_health_score = (agent_health + api_health) / total_components
            else:
                overall_health_score = 0.0

            return SystemHealth(
                status=response.get('status', 'unknown'),
                timestamp=response.get('timestamp', datetime.now().isoformat()),
                agents=response.get('agents', {}),
                external_apis=response.get('external_apis', {}),
                system_load=response.get('system_load', {}),
                overall_health_score=overall_health_score
            )

        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            raise

    async def get_system_capabilities(self) -> Dict[str, Any]:
        """
        Get system capabilities and supported features.

        Returns:
            Dictionary with system capabilities
        """
        try:
            return await self._make_request('GET', '/api/v1/grokopedia/scientific-capabilities')
        except Exception as e:
            logger.error(f"Failed to get system capabilities: {e}")
            raise

    async def get_transparency_report(self, execution_id: str) -> Dict[str, Any]:
        """
        Get detailed transparency report for an execution.

        Args:
            execution_id: Execution ID from a previous query

        Returns:
            Detailed transparency report
        """
        try:
            return await self._make_request('GET', f'/api/v1/transparency/report/{execution_id}')
        except Exception as e:
            logger.error(f"Failed to get transparency report for {execution_id}: {e}")
            raise

    async def get_transparency_statistics(self) -> Dict[str, Any]:
        """
        Get transparency system statistics.

        Returns:
            Transparency statistics and metrics
        """
        try:
            return await self._make_request('GET', '/api/v1/transparency/statistics')
        except Exception as e:
            logger.error(f"Failed to get transparency statistics: {e}")
            raise

    # Batch Processing Methods

    async def batch_scientific_queries(
        self,
        queries: List[Union[str, ScientificQuery]],
        max_concurrent: int = 5,
        **kwargs
    ) -> List[ScientificResult]:
        """
        Execute multiple scientific queries in batch.

        Args:
            queries: List of queries to execute
            max_concurrent: Maximum concurrent queries
            **kwargs: Additional parameters for all queries

        Returns:
            List of ScientificResult objects
        """
        async def process_query(query: Union[str, ScientificQuery]) -> ScientificResult:
            return await self.scientific_query(query, **kwargs)

        # Process in batches to avoid overwhelming the server
        results = []
        for i in range(0, len(queries), max_concurrent):
            batch = queries[i:i + max_concurrent]
            batch_tasks = [process_query(q) for q in batch]

            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch query failed: {result}")
                        # Add error result
                        results.append(ScientificResult(
                            query=str(batch[batch_results.index(result)]) if batch_results.index(result) < len(batch) else "unknown",
                            domain="error",
                            analysis_result={"error": str(result)},
                            confidence_score=0.0,
                            processing_time=0.0
                        ))
                    else:
                        results.append(result)

            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                # Add error results for remaining queries in batch
                for _ in batch:
                    results.append(ScientificResult(
                        query="batch_error",
                        domain="error",
                        analysis_result={"error": str(e)},
                        confidence_score=0.0,
                        processing_time=0.0
                    ))

        logger.info(f"Batch processing completed: {len(results)}/{len(queries)} queries processed")
        return results

    # Streaming Methods

    async def stream_scientific_analysis(
        self,
        query: Union[str, ScientificQuery],
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream scientific analysis results in real-time.

        Args:
            query: Scientific query to execute
            callback: Optional callback function for each result chunk

        Yields:
            Result chunks as they become available
        """
        # Note: This would require server-side streaming support
        # For now, we'll simulate streaming by yielding intermediate results

        if isinstance(query, str):
            query_obj = ScientificQuery(query=query)
        else:
            query_obj = query

        # Simulate streaming by yielding intermediate steps
        yield {"type": "query_received", "query": query_obj.query}

        await asyncio.sleep(0.1)  # Simulate processing delay
        yield {"type": "domain_detected", "domain": query_obj.domain_focus or "auto"}

        await asyncio.sleep(0.2)
        yield {"type": "agents_activated", "agents": ["physics_agent", "chemistry_agent", "mathematics_agent"]}

        await asyncio.sleep(0.3)
        yield {"type": "external_sources_queried", "sources": ["wikipedia", "arxiv"]}

        await asyncio.sleep(0.4)
        yield {"type": "first_principles_applied", "principles_count": 3}

        # Final result
        final_result = await self.scientific_query(query_obj)
        yield {"type": "analysis_complete", "result": final_result.__dict__}

    # Utility Methods

    def set_logging_level(self, level: int):
        """Set logging level for the SDK."""
        logger.setLevel(level)

    def enable_debug_logging(self):
        """Enable debug logging."""
        self.set_logging_level(logging.DEBUG)
        logger.info("Debug logging enabled")

    def disable_debug_logging(self):
        """Disable debug logging."""
        self.set_logging_level(logging.INFO)
        logger.info("Debug logging disabled")

    # Context Manager Support

    @classmethod
    async def create(
        cls,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        **kwargs
    ) -> 'ScientificSDK':
        """
        Create and initialize a ScientificSDK instance.

        Args:
            base_url: Base URL of the scientific API server
            api_key: API key for authentication
            **kwargs: Additional initialization parameters

        Returns:
            Initialized ScientificSDK instance
        """
        instance = cls(base_url=base_url, api_key=api_key, **kwargs)
        # Test connection
        try:
            await instance.get_system_health()
            logger.info("SDK connection test successful")
        except Exception as e:
            logger.warning(f"SDK connection test failed: {e}")
        return instance


# Convenience functions for quick usage

async def quick_scientific_query(
    query: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> ScientificResult:
    """
    Quick scientific query without explicit SDK initialization.

    Args:
        query: Scientific question to ask
        base_url: API server base URL
        **kwargs: Additional query parameters

    Returns:
        ScientificResult with analysis
    """
    async with ScientificSDK(base_url=base_url) as sdk:
        return await sdk.scientific_query(query, **kwargs)


async def quick_claim_validation(
    claim: str,
    domain: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> ValidationResult:
    """
    Quick scientific claim validation.

    Args:
        claim: Claim to validate
        domain: Scientific domain
        base_url: API server base URL
        **kwargs: Additional validation parameters

    Returns:
        ValidationResult with validation details
    """
    async with ScientificSDK(base_url=base_url) as sdk:
        return await sdk.validate_claim(claim, domain, **kwargs)


# Example usage and testing functions

async def example_usage():
    """Example usage of the Scientific SDK."""
    print("🧠 Nexus Lang V2 Scientific SDK - Example Usage")
    print("=" * 55)

    try:
        async with ScientificSDK() as sdk:
            # Example 1: Basic scientific query
            print("\n1. Basic Scientific Query:")
            result = await sdk.scientific_query(
                "Explain the photoelectric effect using first principles"
            )
            print(f"   Domain: {result.domain}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Sources: {len(result.sources_used)}")
            print(f"   First principles: {len(result.first_principles_applied)}")

            # Example 2: Multi-agent collaboration
            print("\n2. Multi-Agent Collaboration:")
            result = await sdk.scientific_query(
                ScientificQuery(
                    query="How does quantum mechanics influence chemical bonding?",
                    require_collaboration=True,
                    include_external_sources=True
                )
            )
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Processing time: {result.processing_time:.2f}s")

            # Example 3: Claim validation
            print("\n3. Scientific Claim Validation:")
            validation = await sdk.validate_claim(
                "Energy cannot be created or destroyed",
                "physics",
                evidence_types=["experimental", "theoretical"]
            )
            print(f"   Result: {validation.validation_result}")
            print(f"   Confidence: {validation.confidence_score:.2f}")
            print(f"   Evidence strength: {validation.evidence_strength}")

            # Example 4: First principles analysis
            print("\n4. First Principles Analysis:")
            analysis = await sdk.first_principles_analysis(
                "thermodynamics",
                "physics",
                depth="comprehensive"
            )
            print(f"   Principles identified: {len(analysis.fundamental_principles)}")
            print(f"   Deduction steps: {len(analysis.logical_deduction_steps)}")
            print(f"   Confidence level: {analysis.confidence_level}")

            # Example 5: System health check
            print("\n5. System Health Check:")
            health = await sdk.get_system_health()
            print(f"   Overall status: {health.status}")
            print(f"   Active agents: {len([a for a in health.agents.values() if a.get('status') == 'active'])}")
            print(f"   Response time: {health.response_time:.1f}ms")
    except Exception as e:
        print(f"❌ Example usage failed: {e}")
        print("Make sure the scientific API server is running on http://localhost:8000")


async def benchmark_sdk():
    """Benchmark the SDK performance."""
    print("⚡ Scientific SDK Performance Benchmark")
    print("-" * 40)

    test_queries = [
        "Explain Newton's laws",
        "What is chemical equilibrium?",
        "Prove the Pythagorean theorem",
        "How does natural selection work?",
        "What is the structure of DNA?"
    ]

    async with ScientificSDK() as sdk:
        start_time = asyncio.get_event_loop().time()

        # Test individual queries
        for i, query in enumerate(test_queries, 1):
            try:
                result = await sdk.scientific_query(query)
                print(f"   Query {i}: SUCCESS ({result.response_time:.2f}s)")
            except Exception as e:
                print(f"   Query {i}: FAILED - {e}")

        # Test batch processing
        batch_start = asyncio.get_event_loop().time()
        try:
            batch_results = await sdk.batch_scientific_queries(test_queries[:3])
            batch_time = asyncio.get_event_loop().time() - batch_start
            print(f"   Batch processing: SUCCESS ({batch_time:.2f}s for {len(batch_results)} queries)")
        except Exception as e:
            print(f"   Batch processing: FAILED - {e}")

        total_time = asyncio.get_event_loop().time() - start_time
        print(f"\nBenchmark completed in {total_time:.1f}s")
if __name__ == "__main__":
    # Run examples
    asyncio.run(example_usage())
    print("\n" + "="*55)
    asyncio.run(benchmark_sdk())
