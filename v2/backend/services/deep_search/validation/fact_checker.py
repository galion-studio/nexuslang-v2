"""
Fact Checker for Deep Search Validation
Cross-references and validates facts across multiple sources
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of fact validation"""
    fact: str
    confidence_score: float
    supporting_sources: int
    contradicting_sources: int
    validation_level: str  # 'high', 'medium', 'low', 'uncertain'
    cross_references: List[Dict[str, Any]]
    flags: List[str]  # 'outdated', 'biased', 'inconsistent', etc.


@dataclass
class ValidationReport:
    """Complete validation report for a set of facts"""
    overall_confidence: float
    facts_validated: int
    high_confidence_facts: int
    medium_confidence_facts: int
    low_confidence_facts: int
    uncertain_facts: int
    validation_results: List[ValidationResult]
    recommendations: List[str]


class FactChecker:
    """
    Fact checking system for validating research information

    Features:
    - Cross-source validation
    - Temporal consistency checking
    - Source credibility assessment
    - Contradiction detection
    - Confidence scoring
    """

    def __init__(self):
        self.validation_rules = {
            "temporal_consistency": self._check_temporal_consistency,
            "source_credibility": self._assess_source_credibility,
            "cross_reference": self._perform_cross_reference,
            "contradiction_detection": self._detect_contradictions,
            "factual_accuracy": self._check_factual_accuracy
        }

        logger.info("Initialized fact checker")

    async def validate_facts(self, facts: List[str], sources: List[Dict[str, Any]],
                           validation_level: str = "comprehensive") -> ValidationReport:
        """
        Validate a list of facts against multiple sources

        Args:
            facts: List of facts to validate
            sources: List of source information
            validation_level: 'basic', 'comprehensive', 'exhaustive'

        Returns:
            ValidationReport with detailed results
        """
        try:
            validation_results = []

            for fact in facts:
                result = await self._validate_single_fact(fact, sources, validation_level)
                validation_results.append(result)

            # Generate overall report
            report = self._generate_validation_report(validation_results)

            logger.info(f"Fact validation completed: {len(facts)} facts validated")
            return report

        except Exception as e:
            logger.error(f"Fact validation failed: {e}")
            return ValidationReport(
                overall_confidence=0.0,
                facts_validated=0,
                high_confidence_facts=0,
                medium_confidence_facts=0,
                low_confidence_facts=0,
                uncertain_facts=0,
                validation_results=[],
                recommendations=["Validation system error occurred"]
            )

    async def _validate_single_fact(self, fact: str, sources: List[Dict[str, Any]],
                                  validation_level: str) -> ValidationResult:
        """Validate a single fact"""
        supporting_sources = 0
        contradicting_sources = 0
        cross_references = []
        flags = []

        # Find relevant sources for this fact
        relevant_sources = self._find_relevant_sources(fact, sources)

        if not relevant_sources:
            return ValidationResult(
                fact=fact,
                confidence_score=0.0,
                supporting_sources=0,
                contradicting_sources=0,
                validation_level="uncertain",
                cross_references=[],
                flags=["no_sources_found"]
            )

        # Apply validation rules based on level
        validation_methods = self._get_validation_methods(validation_level)

        for method in validation_methods:
            try:
                result = await method(fact, relevant_sources)
                supporting_sources += result.get("supporting", 0)
                contradicting_sources += result.get("contradicting", 0)
                cross_references.extend(result.get("references", []))
                flags.extend(result.get("flags", []))
            except Exception as e:
                logger.warning(f"Validation method {method.__name__} failed: {e}")

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            supporting_sources, contradicting_sources, len(relevant_sources)
        )

        # Determine validation level
        validation_level_result = self._determine_validation_level(confidence_score, flags)

        return ValidationResult(
            fact=fact,
            confidence_score=confidence_score,
            supporting_sources=supporting_sources,
            contradicting_sources=contradicting_sources,
            validation_level=validation_level_result,
            cross_references=cross_references,
            flags=list(set(flags))  # Remove duplicates
        )

    def _find_relevant_sources(self, fact: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find sources that are relevant to the fact"""
        relevant_sources = []
        fact_lower = fact.lower()

        # Extract key terms from fact (simple approach)
        key_terms = self._extract_key_terms(fact)

        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()

            # Check if source contains key terms
            relevance_score = 0
            for term in key_terms:
                if term in content or term in title:
                    relevance_score += 1

            # Consider source relevant if it contains at least 50% of key terms
            if relevance_score >= len(key_terms) * 0.5:
                source_copy = source.copy()
                source_copy['relevance_score'] = relevance_score
                relevant_sources.append(source_copy)

        # Sort by relevance score
        relevant_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return relevant_sources[:10]  # Limit to top 10 most relevant

    def _extract_key_terms(self, fact: str) -> List[str]:
        """Extract key terms from a fact for matching"""
        # Remove common stop words and punctuation
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}

        # Simple tokenization and cleaning
        words = re.findall(r'\b\w+\b', fact.lower())
        key_terms = [word for word in words if len(word) > 2 and word not in stop_words]

        return list(set(key_terms))  # Remove duplicates

    def _get_validation_methods(self, validation_level: str) -> List[callable]:
        """Get validation methods based on level"""
        if validation_level == "basic":
            return [self.validation_rules["source_credibility"]]
        elif validation_level == "comprehensive":
            return [
                self.validation_rules["source_credibility"],
                self.validation_rules["cross_reference"],
                self.validation_rules["temporal_consistency"]
            ]
        else:  # exhaustive
            return list(self.validation_rules.values())

    async def _check_temporal_consistency(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if information is temporally consistent"""
        result = {"supporting": 0, "contradicting": 0, "references": [], "flags": []}

        # Look for dates or time references in fact and sources
        fact_dates = self._extract_dates(fact)

        for source in sources:
            source_dates = self._extract_dates(source.get('content', ''))

            if fact_dates and source_dates:
                # Check if dates are consistent (simplified check)
                consistency = self._check_date_consistency(fact_dates, source_dates)

                if consistency == "consistent":
                    result["supporting"] += 1
                elif consistency == "inconsistent":
                    result["contradicting"] += 1
                    result["flags"].append("temporal_inconsistency")

                result["references"].append({
                    "source": source.get('title', 'Unknown'),
                    "consistency": consistency,
                    "fact_dates": fact_dates,
                    "source_dates": source_dates
                })

        return result

    async def _assess_source_credibility(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the credibility of sources"""
        result = {"supporting": 0, "contradicting": 0, "references": [], "flags": []}

        for source in sources:
            credibility_score = self._calculate_source_credibility(source)

            if credibility_score >= 0.7:
                result["supporting"] += 1
            elif credibility_score < 0.4:
                result["contradicting"] += 1
                result["flags"].append("low_credibility_source")

            result["references"].append({
                "source": source.get('title', 'Unknown'),
                "credibility_score": credibility_score,
                "assessment": "high" if credibility_score >= 0.7 else "medium" if credibility_score >= 0.4 else "low"
            })

        return result

    async def _perform_cross_reference(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform cross-referencing between sources"""
        result = {"supporting": 0, "contradicting": 0, "references": [], "flags": []}

        if len(sources) < 2:
            return result

        # Check how many sources agree on the fact
        agreements = 0
        total_comparisons = 0

        for i, source1 in enumerate(sources):
            for source2 in sources[i+1:]:
                total_comparisons += 1
                agreement = self._check_source_agreement(fact, source1, source2)

                if agreement:
                    agreements += 1
                else:
                    result["flags"].append("source_disagreement")

        # Calculate agreement ratio
        agreement_ratio = agreements / max(total_comparisons, 1)

        if agreement_ratio >= 0.7:
            result["supporting"] = len(sources)
        elif agreement_ratio < 0.3:
            result["contradicting"] = len(sources) // 2

        result["references"].append({
            "cross_reference_type": "source_agreement",
            "agreement_ratio": agreement_ratio,
            "total_comparisons": total_comparisons,
            "agreements": agreements
        })

        return result

    async def _detect_contradictions(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect contradictions in sources"""
        result = {"supporting": 0, "contradicting": 0, "references": [], "flags": []}

        contradictions = []

        # Simple contradiction detection (would be enhanced with NLP)
        fact_lower = fact.lower()

        for source in sources:
            content = source.get('content', '').lower()

            # Look for negation patterns near key terms
            key_terms = self._extract_key_terms(fact)
            contradiction_found = False

            for term in key_terms:
                if term in content:
                    # Check for negation words near the term
                    term_index = content.find(term)
                    if term_index != -1:
                        # Check surrounding context for negations
                        context_start = max(0, term_index - 50)
                        context_end = min(len(content), term_index + len(term) + 50)
                        context = content[context_start:context_end]

                        negation_words = ['not', 'no', 'never', 'none', 'without', 'except', 'but', 'however']
                        if any(neg_word in context for neg_word in negation_words):
                            contradiction_found = True
                            break

            if contradiction_found:
                contradictions.append(source.get('title', 'Unknown'))
                result["contradicting"] += 1
            else:
                result["supporting"] += 1

        if contradictions:
            result["flags"].append("contradictions_detected")
            result["references"].append({
                "contradiction_type": "negation_detected",
                "contradicting_sources": contradictions
            })

        return result

    async def _check_factual_accuracy(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check factual accuracy using basic heuristics"""
        result = {"supporting": 0, "contradicting": 0, "references": [], "flags": []}

        # Basic factual checks (would be enhanced with knowledge bases)
        fact_checks = [
            self._check_number_consistency,
            self._check_logical_consistency,
            self._check_common_factual_errors
        ]

        for check_func in fact_checks:
            check_result = check_func(fact, sources)
            result["supporting"] += check_result.get("supporting", 0)
            result["contradicting"] += check_result.get("contradicting", 0)
            result["flags"].extend(check_result.get("flags", []))

        return result

    def _extract_dates(self, text: str) -> List[str]:
        """Extract date patterns from text"""
        # Simple date pattern matching
        date_patterns = [
            r'\b\d{4}\b',  # Years like 2023
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)

        return list(set(dates))  # Remove duplicates

    def _check_date_consistency(self, fact_dates: List[str], source_dates: List[str]) -> str:
        """Check if dates are consistent"""
        if not fact_dates or not source_dates:
            return "unknown"

        # Simple check: if any dates overlap, consider consistent
        for fact_date in fact_dates:
            for source_date in source_dates:
                if fact_date == source_date:
                    return "consistent"

        # If no exact matches but dates exist, consider potentially consistent
        return "potentially_consistent"

    def _calculate_source_credibility(self, source: Dict[str, Any]) -> float:
        """Calculate credibility score for a source"""
        credibility = 0.5  # Base score

        # Verified sources get higher score
        if source.get('verified', False):
            credibility += 0.3

        # Recent sources get slight boost
        created_at = source.get('created_at')
        if isinstance(created_at, str):
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.utcnow() - created_date).days
                if days_old < 365:  # Less than a year old
                    credibility += 0.1
                elif days_old > 365 * 5:  # More than 5 years old
                    credibility -= 0.1
            except:
                pass

        # Sources with more content get slight boost
        content_length = len(source.get('content', ''))
        if content_length > 1000:
            credibility += 0.1

        return max(0.0, min(1.0, credibility))

    def _check_source_agreement(self, fact: str, source1: Dict[str, Any], source2: Dict[str, Any]) -> bool:
        """Check if two sources agree on a fact"""
        # Simple agreement check based on key terms
        key_terms = self._extract_key_terms(fact)

        content1 = source1.get('content', '').lower()
        content2 = source2.get('content', '').lower()

        # Count how many key terms appear in both sources
        agreement_score = 0
        for term in key_terms:
            if term in content1 and term in content2:
                agreement_score += 1

        # Consider sources in agreement if they share most key terms
        return agreement_score >= len(key_terms) * 0.6

    def _check_number_consistency(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check consistency of numbers in fact across sources"""
        result = {"supporting": 0, "contradicting": 0, "flags": []}

        # Extract numbers from fact
        fact_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', fact)

        if not fact_numbers:
            return result

        for source in sources:
            content = source.get('content', '')
            source_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', content)

            # Check if fact numbers appear in source
            matches = 0
            for fact_num in fact_numbers:
                if fact_num in source_numbers:
                    matches += 1

            if matches >= len(fact_numbers) * 0.5:  # At least 50% match
                result["supporting"] += 1
            else:
                result["contradicting"] += 1
                result["flags"].append("number_inconsistency")

        return result

    def _check_logical_consistency(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check logical consistency of the fact"""
        result = {"supporting": 0, "contradicting": 0, "flags": []}

        # Basic logical checks (would be enhanced with more sophisticated logic)
        logical_issues = []

        # Check for obviously impossible statements
        fact_lower = fact.lower()
        if "square circle" in fact_lower or "married bachelor" in fact_lower:
            logical_issues.append("logical_contradiction")

        if logical_issues:
            result["contradicting"] = len(sources)  # All sources contradict logical impossibility
            result["flags"].extend(logical_issues)

        return result

    def _check_common_factual_errors(self, fact: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for common factual errors"""
        result = {"supporting": 0, "contradicting": 0, "flags": []}

        # Common factual corrections (very basic example)
        corrections = {
            "the capital of france is london": "geographical_error",
            "water boils at 0 degrees": "scientific_error",
            "the earth is flat": "scientific_error"
        }

        fact_lower = fact.lower()
        for error_pattern, error_type in corrections.items():
            if error_pattern in fact_lower:
                result["contradicting"] = len(sources)
                result["flags"].append(error_type)
                break

        return result

    def _calculate_confidence_score(self, supporting: int, contradicting: int, total_sources: int) -> float:
        """Calculate confidence score based on source agreement"""
        if total_sources == 0:
            return 0.0

        agreement_ratio = supporting / total_sources
        contradiction_penalty = contradicting / total_sources

        confidence = agreement_ratio - contradiction_penalty * 0.5
        return max(0.0, min(1.0, confidence))

    def _determine_validation_level(self, confidence_score: float, flags: List[str]) -> str:
        """Determine validation level based on confidence and flags"""
        # Check for critical flags
        critical_flags = ['logical_contradiction', 'scientific_error', 'geographical_error']
        if any(flag in critical_flags for flag in flags):
            return "contradicted"

        if confidence_score >= 0.8:
            return "high"
        elif confidence_score >= 0.6:
            return "medium"
        elif confidence_score >= 0.3:
            return "low"
        else:
            return "uncertain"

    def _generate_validation_report(self, validation_results: List[ValidationResult]) -> ValidationReport:
        """Generate comprehensive validation report"""
        if not validation_results:
            return ValidationReport(
                overall_confidence=0.0,
                facts_validated=0,
                high_confidence_facts=0,
                medium_confidence_facts=0,
                low_confidence_facts=0,
                uncertain_facts=0,
                validation_results=[],
                recommendations=[]
            )

        # Calculate statistics
        high_confidence = sum(1 for r in validation_results if r.validation_level == "high")
        medium_confidence = sum(1 for r in validation_results if r.validation_level == "medium")
        low_confidence = sum(1 for r in validation_results if r.validation_level == "low")
        uncertain = sum(1 for r in validation_results if r.validation_level in ["uncertain", "contradicted"])

        # Overall confidence is weighted average
        total_confidence = sum(r.confidence_score for r in validation_results)
        overall_confidence = total_confidence / len(validation_results)

        # Generate recommendations
        recommendations = []
        if overall_confidence < 0.5:
            recommendations.append("Consider additional sources for validation")
        if uncertain > len(validation_results) * 0.3:
            recommendations.append("Many facts have low confidence - verify with authoritative sources")
        if high_confidence < len(validation_results) * 0.2:
            recommendations.append("Limited high-confidence information found")

        return ValidationReport(
            overall_confidence=overall_confidence,
            facts_validated=len(validation_results),
            high_confidence_facts=high_confidence,
            medium_confidence_facts=medium_confidence,
            low_confidence_facts=low_confidence,
            uncertain_facts=uncertain,
            validation_results=validation_results,
            recommendations=recommendations
        )
