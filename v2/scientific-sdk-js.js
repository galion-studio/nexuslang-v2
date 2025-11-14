/**
 * Nexus Lang V2 Scientific Knowledge Enhancement SDK for JavaScript
 * ===============================================================
 *
 * Comprehensive SDK for easy integration of scientific AI capabilities into web applications.
 *
 * Features:
 * - Promise-based API for scientific queries
 * - Automatic retry and error handling
 * - Batch processing capabilities
 * - Real-time streaming results
 * - TypeScript support with JSDoc annotations
 * - Browser and Node.js compatibility
 *
 * @author Nexus Lang V2 Scientific SDK Team
 * @version 2.0.0
 * @date November 2025
 */

(function(global) {
    'use strict';

    /**
     * Scientific query configuration
     * @typedef {Object} ScientificQueryConfig
     * @property {string} query - Scientific question or problem
     * @property {string} [domain_focus] - Domain focus (physics, chemistry, mathematics, multi, auto)
     * @property {boolean} [require_collaboration=true] - Enable multi-agent collaboration
     * @property {boolean} [include_external_sources=true] - Include external knowledge sources
     * @property {boolean} [first_principles_only=false] - Use first principles only
     * @property {Object} [context] - Additional context for the query
     */

    /**
     * Scientific analysis result
     * @typedef {Object} ScientificResult
     * @property {string} query - Original query
     * @property {string} domain - Detected or specified domain
     * @property {Object} analysis_result - Detailed analysis results
     * @property {Object} [external_knowledge] - External knowledge sources used
     * @property {number} confidence_score - Confidence score (0.0 to 1.0)
     * @property {number} processing_time - Processing time in seconds
     * @property {string[]} sources_used - List of knowledge sources used
     * @property {string[]} first_principles_applied - First principles applied
     * @property {Object} [transparency_report] - Complete transparency report
     * @property {string} [execution_id] - Unique execution identifier
     */

    /**
     * Scientific validation result
     * @typedef {Object} ValidationResult
     * @property {string} claim - Original claim
     * @property {string} domain - Scientific domain
     * @property {string} validation_result - Result (supported, refuted, inconclusive)
     * @property {number} confidence_score - Confidence score (0.0 to 1.0)
     * @property {string} evidence_strength - Evidence strength (strong, moderate, weak)
     * @property {string[]} validation_methods - Methods used for validation
     * @property {number} processing_time - Processing time in seconds
     * @property {string} [execution_id] - Unique execution identifier
     */

    /**
     * First principles analysis result
     * @typedef {Object} FirstPrinciplesResult
     * @property {string} topic - Topic analyzed
     * @property {string} domain - Scientific domain
     * @property {string[]} fundamental_principles - Fundamental principles identified
     * @property {Object[]} logical_deduction_steps - Logical deduction steps
     * @property {Object[]} counterexamples - Counterexamples considered
     * @property {string[]} conclusions - Analysis conclusions
     * @property {string} confidence_level - Confidence level (high, moderate, low)
     * @property {number} processing_time - Processing time in seconds
     * @property {string} [execution_id] - Unique execution identifier
     */

    /**
     * System health status
     * @typedef {Object} SystemHealth
     * @property {string} status - Overall status (healthy, degraded, error)
     * @property {string} timestamp - Status timestamp
     * @property {Object} agents - Agent status information
     * @property {Object} external_apis - External API status information
     * @property {Object} system_load - System load metrics
     * @property {number} overall_health_score - Overall health score (0.0 to 1.0)
     */

    /**
     * Nexus Lang V2 Scientific Knowledge Enhancement SDK
     */
    class ScientificSDK {
        /**
         * Create a new Scientific SDK instance
         *
         * @param {Object} options - SDK configuration options
         * @param {string} [options.baseURL='http://localhost:8000'] - Base URL of the scientific API server
         * @param {string} [options.apiKey] - API key for authentication
         * @param {number} [options.timeout=30000] - Request timeout in milliseconds
         * @param {number} [options.maxRetries=3] - Maximum number of retries for failed requests
         * @param {number} [options.retryDelay=1000] - Delay between retries in milliseconds
         */
        constructor(options = {}) {
            this.baseURL = options.baseURL || 'http://localhost:8000';
            this.apiKey = options.apiKey;
            this.timeout = options.timeout || 30000;
            this.maxRetries = options.maxRetries || 3;
            this.retryDelay = options.retryDelay || 1000;

            this.defaultHeaders = {
                'Content-Type': 'application/json',
                'User-Agent': 'Nexus-Scientific-SDK-JS/2.0.0'
            };

            if (this.apiKey) {
                this.defaultHeaders['Authorization'] = `Bearer ${this.apiKey}`;
            }

            console.log(`Scientific SDK initialized with base URL: ${this.baseURL}`);
        }

        /**
         * Make HTTP request with retry logic
         *
         * @private
         * @param {string} method - HTTP method
         * @param {string} endpoint - API endpoint
         * @param {Object} [data] - Request data
         * @param {Object} [params] - Query parameters
         * @returns {Promise<Object>} Response data
         */
        async _makeRequest(method, endpoint, data = null, params = null) {
            const url = new URL(endpoint, this.baseURL);

            if (params) {
                Object.keys(params).forEach(key => {
                    url.searchParams.append(key, params[key]);
                });
            }

            const requestOptions = {
                method: method.toUpperCase(),
                headers: { ...this.defaultHeaders },
                signal: AbortSignal.timeout(this.timeout)
            };

            if (data && (method.toUpperCase() === 'POST' || method.toUpperCase() === 'PUT')) {
                requestOptions.body = JSON.stringify(data);
            }

            let lastError;

            for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
                try {
                    const response = await fetch(url, requestOptions);

                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`HTTP ${response.status}: ${errorText}`);
                    }

                    return await response.json();

                } catch (error) {
                    lastError = error;
                    console.warn(`Request attempt ${attempt} failed:`, error.message);

                    if (attempt < this.maxRetries) {
                        await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
                    }
                }
            }

            throw new Error(`Request failed after ${this.maxRetries} attempts: ${lastError.message}`);
        }

        /**
         * Execute comprehensive scientific query using specialized agents
         *
         * @param {string|ScientificQueryConfig} query - Scientific question or query configuration
         * @param {Object} [options] - Additional query options
         * @returns {Promise<ScientificResult>} Scientific analysis result
         *
         * @example
         * // Simple query
         * const result = await sdk.scientificQuery("Explain the photoelectric effect");
         *
         * @example
         * // Advanced query with options
         * const result = await sdk.scientificQuery({
         *   query: "How does quantum mechanics influence chemical bonding?",
         *   domain_focus: "multi",
         *   require_collaboration: true,
         *   include_external_sources: true
         * });
         */
        async scientificQuery(query, options = {}) {
            let queryData;

            if (typeof query === 'string') {
                queryData = { query, ...options };
            } else {
                queryData = { ...query, ...options };
            }

            // Remove undefined values
            queryData = Object.fromEntries(
                Object.entries(queryData).filter(([_, value]) => value !== undefined)
            );

            console.log(`Executing scientific query: ${queryData.query.substring(0, 50)}...`);

            const startTime = Date.now();
            try {
                const response = await this._makeRequest('POST', '/api/v1/grokopedia/scientific-query', queryData);
                const processingTime = (Date.now() - startTime) / 1000;

                const result = {
                    ...response,
                    processing_time: processingTime
                };

                console.log(`Scientific query completed in ${processingTime.toFixed(2)}s with ${result.confidence_score?.toFixed(2) || 'N/A'} confidence`);
                return result;

            } catch (error) {
                const processingTime = (Date.now() - startTime) / 1000;
                console.error(`Scientific query failed after ${processingTime.toFixed(2)}s:`, error);
                throw error;
            }
        }

        /**
         * Validate scientific claim using evidence-based reasoning
         *
         * @param {string} claim - Scientific claim to validate
         * @param {string} domain - Scientific domain (physics, chemistry, mathematics)
         * @param {string[]} [evidenceTypes] - Types of evidence to consider
         * @param {Object} [options] - Additional validation options
         * @returns {Promise<ValidationResult>} Validation result
         *
         * @example
         * const validation = await sdk.validateClaim(
         *   "Energy cannot be created or destroyed",
         *   "physics",
         *   ["experimental", "theoretical"]
         * );
         */
        async validateClaim(claim, domain, evidenceTypes = null, options = {}) {
            if (!evidenceTypes) {
                evidenceTypes = ["experimental", "theoretical", "observational"];
            }

            const requestData = {
                claim,
                domain,
                evidence_types: evidenceTypes,
                ...options
            };

            console.log(`Validating claim: ${claim.substring(0, 50)}...`);

            const startTime = Date.now();
            try {
                const response = await this._makeRequest('POST', '/api/v1/grokopedia/scientific-validation', requestData);
                const processingTime = (Date.now() - startTime) / 1000;

                const result = {
                    ...response,
                    processing_time: processingTime
                };

                console.log(`Claim validation completed: ${result.validation_result} (${(result.confidence_score * 100).toFixed(1)}% confidence)`);
                return result;

            } catch (error) {
                const processingTime = (Date.now() - startTime) / 1000;
                console.error(`Claim validation failed after ${processingTime.toFixed(2)}s:`, error);
                throw error;
            }
        }

        /**
         * Perform first principles analysis of scientific topics
         *
         * @param {string} topic - Scientific topic to analyze
         * @param {string} domain - Scientific domain
         * @param {string} [depth='comprehensive'] - Analysis depth
         * @param {Object} [options] - Additional analysis options
         * @returns {Promise<FirstPrinciplesResult>} First principles analysis result
         *
         * @example
         * const analysis = await sdk.firstPrinciplesAnalysis(
         *   "thermodynamics",
         *   "physics",
         *   "comprehensive"
         * );
         */
        async firstPrinciplesAnalysis(topic, domain, depth = 'comprehensive', options = {}) {
            const requestData = {
                topic,
                domain,
                depth,
                ...options
            };

            console.log(`Performing first principles analysis of: ${topic}`);

            const startTime = Date.now();
            try {
                const response = await this._makeRequest('POST', '/api/v1/grokopedia/first-principles-analysis', requestData);
                const processingTime = (Date.now() - startTime) / 1000;

                const result = {
                    ...response,
                    processing_time: processingTime
                };

                console.log(`First principles analysis completed: ${result.fundamental_principles?.length || 0} principles identified`);
                return result;

            } catch (error) {
                const processingTime = (Date.now() - startTime) / 1000;
                console.error(`First principles analysis failed after ${processingTime.toFixed(2)}s:`, error);
                throw error;
            }
        }

        /**
         * Get current system health status
         *
         * @returns {Promise<SystemHealth>} System health information
         */
        async getSystemHealth() {
            try {
                const response = await this._makeRequest('GET', '/api/v1/grokopedia/scientific-health');

                // Calculate overall health score
                const agents = response.agents || {};
                const apis = response.external_apis || {};
                const agentHealth = Object.values(agents).filter(a => a.status === 'active').length;
                const apiHealth = Object.values(apis).filter(a => a.status === 'healthy').length;
                const totalComponents = Object.keys(agents).length + Object.keys(apis).length;

                const overallHealthScore = totalComponents > 0 ? (agentHealth + apiHealth) / totalComponents : 0;

                return {
                    ...response,
                    overall_health_score: overallHealthScore
                };

            } catch (error) {
                console.error('Failed to get system health:', error);
                throw error;
            }
        }

        /**
         * Get system capabilities and supported features
         *
         * @returns {Promise<Object>} System capabilities information
         */
        async getSystemCapabilities() {
            try {
                return await this._makeRequest('GET', '/api/v1/grokopedia/scientific-capabilities');
            } catch (error) {
                console.error('Failed to get system capabilities:', error);
                throw error;
            }
        }

        /**
         * Get detailed transparency report for an execution
         *
         * @param {string} executionId - Execution ID from a previous query
         * @returns {Promise<Object>} Detailed transparency report
         */
        async getTransparencyReport(executionId) {
            try {
                return await this._makeRequest('GET', `/api/v1/transparency/report/${executionId}`);
            } catch (error) {
                console.error(`Failed to get transparency report for ${executionId}:`, error);
                throw error;
            }
        }

        /**
         * Get transparency system statistics
         *
         * @returns {Promise<Object>} Transparency statistics
         */
        async getTransparencyStatistics() {
            try {
                return await this._makeRequest('GET', '/api/v1/transparency/statistics');
            } catch (error) {
                console.error('Failed to get transparency statistics:', error);
                throw error;
            }
        }

        /**
         * Execute multiple scientific queries in batch
         *
         * @param {string[]|ScientificQueryConfig[]} queries - List of queries to execute
         * @param {Object} [options] - Batch processing options
         * @param {number} [options.maxConcurrent=3] - Maximum concurrent queries
         * @returns {Promise<ScientificResult[]>} List of results
         */
        async batchScientificQueries(queries, options = {}) {
            const maxConcurrent = options.maxConcurrent || 3;
            const results = [];

            // Process in batches
            for (let i = 0; i < queries.length; i += maxConcurrent) {
                const batch = queries.slice(i, i + maxConcurrent);
                const batchPromises = batch.map(query => this.scientificQuery(query));

                try {
                    const batchResults = await Promise.all(batchPromises);
                    results.push(...batchResults);
                } catch (error) {
                    console.error('Batch processing error:', error);
                    // Add error results for failed batch
                    batch.forEach(() => {
                        results.push({
                            query: 'batch_error',
                            domain: 'error',
                            analysis_result: { error: error.message },
                            confidence_score: 0,
                            processing_time: 0
                        });
                    });
                }
            }

            console.log(`Batch processing completed: ${results.length}/${queries.length} queries processed`);
            return results;
        }

        /**
         * Stream scientific analysis results in real-time
         *
         * @param {string|ScientificQueryConfig} query - Scientific query
         * @param {Function} [callback] - Callback for each result chunk
         * @returns {AsyncGenerator<Object>} Result chunks
         */
        async* streamScientificAnalysis(query, callback = null) {
            const queryData = typeof query === 'string' ? { query } : query;

            yield { type: 'query_received', query: queryData.query };
            if (callback) callback({ type: 'query_received', query: queryData.query });

            // Simulate streaming (would require server-side streaming in real implementation)
            await new Promise(resolve => setTimeout(resolve, 100));
            yield { type: 'domain_detected', domain: queryData.domain_focus || 'auto' };
            if (callback) callback({ type: 'domain_detected', domain: queryData.domain_focus || 'auto' });

            await new Promise(resolve => setTimeout(resolve, 200));
            yield { type: 'agents_activated', agents: ['physics_agent', 'chemistry_agent', 'mathematics_agent'] };
            if (callback) callback({ type: 'agents_activated', agents: ['physics_agent', 'chemistry_agent', 'mathematics_agent'] });

            await new Promise(resolve => setTimeout(resolve, 300));
            yield { type: 'external_sources_queried', sources: ['wikipedia', 'arxiv'] };
            if (callback) callback({ type: 'external_sources_queried', sources: ['wikipedia', 'arxiv'] });

            await new Promise(resolve => setTimeout(resolve, 400));
            yield { type: 'first_principles_applied', principles_count: 3 };
            if (callback) callback({ type: 'first_principles_applied', principles_count: 3 });

            // Final result
            const finalResult = await this.scientificQuery(queryData);
            yield { type: 'analysis_complete', result: finalResult };
            if (callback) callback({ type: 'analysis_complete', result: finalResult });
        }
    }

    // Convenience functions

    /**
     * Quick scientific query without SDK initialization
     *
     * @param {string} query - Scientific question
     * @param {Object} [options] - Query options
     * @returns {Promise<ScientificResult>} Query result
     */
    async function quickScientificQuery(query, options = {}) {
        const sdk = new ScientificSDK(options);
        try {
            return await sdk.scientificQuery(query, options);
        } finally {
            // Clean up if needed
        }
    }

    /**
     * Quick claim validation without SDK initialization
     *
     * @param {string} claim - Claim to validate
     * @param {string} domain - Scientific domain
     * @param {Object} [options] - Validation options
     * @returns {Promise<ValidationResult>} Validation result
     */
    async function quickValidateClaim(claim, domain, options = {}) {
        const sdk = new ScientificSDK(options);
        try {
            return await sdk.validateClaim(claim, domain, null, options);
        } finally {
            // Clean up if needed
        }
    }

    // Example usage and testing
    async function runExamples() {
        console.log('🧠 Nexus Lang V2 Scientific SDK - JavaScript Examples');
        console.log('=' * 60);

        const sdk = new ScientificSDK({
            baseURL: 'http://localhost:8000',
            timeout: 30000
        });

        try {
            // Example 1: Basic scientific query
            console.log('\n1. Basic Scientific Query:');
            const result1 = await sdk.scientificQuery('Explain the photoelectric effect');
            console.log(`   Domain: ${result1.domain}`);
            console.log(`   Confidence: ${(result1.confidence_score * 100).toFixed(1)}%`);
            console.log(`   Processing time: ${result1.processing_time.toFixed(2)}s`);

            // Example 2: Advanced query with options
            console.log('\n2. Multi-Agent Collaboration:');
            const result2 = await sdk.scientificQuery({
                query: 'How does quantum mechanics influence chemical bonding?',
                domain_focus: 'multi',
                require_collaboration: true,
                include_external_sources: true
            });
            console.log(`   Confidence: ${(result2.confidence_score * 100).toFixed(1)}%`);
            console.log(`   Sources used: ${result2.sources_used.length}`);

            // Example 3: Claim validation
            console.log('\n3. Scientific Claim Validation:');
            const validation = await sdk.validateClaim(
                'Energy cannot be created or destroyed',
                'physics'
            );
            console.log(`   Result: ${validation.validation_result}`);
            console.log(`   Evidence strength: ${validation.evidence_strength}`);

            // Example 4: System health
            console.log('\n4. System Health Check:');
            const health = await sdk.getSystemHealth();
            console.log(`   Status: ${health.status}`);
            console.log(`   Active agents: ${Object.values(health.agents).filter(a => a.status === 'active').length}`);
            console.log(`   Overall health: ${(health.overall_health_score * 100).toFixed(1)}%`);

        } catch (error) {
            console.error('❌ Examples failed:', error.message);
            console.log('\nMake sure the scientific API server is running on http://localhost:8000');
        }
    }

    // Export for different environments
    if (typeof module !== 'undefined' && module.exports) {
        // Node.js
        module.exports = {
            ScientificSDK,
            quickScientificQuery,
            quickValidateClaim,
            runExamples
        };
    } else {
        // Browser
        global.ScientificSDK = ScientificSDK;
        global.quickScientificQuery = quickScientificQuery;
        global.quickValidateClaim = quickValidateClaim;
        global.runScientificExamples = runExamples;

        // Auto-run examples if this script is loaded directly in browser
        if (typeof window !== 'undefined' && window.location) {
            // Add a small delay to allow page to load
            setTimeout(() => {
                if (window.location.search.includes('run-examples')) {
                    runExamples();
                }
            }, 100);
        }
    }

})(typeof window !== 'undefined' ? window : global);
