"""
Transparency Service for Agent Decision-Making and Knowledge Sourcing

This service provides:
- Complete traceability of agent reasoning processes
- Source verification and validation tracking
- First principles application logging
- Confidence score calculation and justification
- Audit trail for scientific claims and validations

Built for maximum transparency in AI decision-making processes.
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

from .agents.base_agent import AgentResult


@dataclass
class ReasoningStep:
    """Represents a single step in an agent's reasoning process."""
    step_id: str
    agent_name: str
    timestamp: datetime
    step_type: str  # input_processing, knowledge_retrieval, reasoning, validation, conclusion
    description: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    confidence_score: float
    sources_used: List[str]
    first_principles_applied: List[str]
    processing_time: float
    metadata: Dict[str, Any]


@dataclass
class KnowledgeSource:
    """Represents a source of knowledge used in reasoning."""
    source_id: str
    source_type: str  # internal_agent, external_api, knowledge_base, first_principles
    source_name: str
    url: Optional[str]
    timestamp: datetime
    content_hash: str
    reliability_score: float
    domain: str
    metadata: Dict[str, Any]


@dataclass
class ValidationRecord:
    """Records validation of scientific claims or reasoning."""
    validation_id: str
    claim: str
    validation_type: str  # first_principles, empirical, logical, consistency
    validator_agent: str
    validation_result: str  # supported, refuted, inconclusive
    evidence_used: List[str]
    counter_evidence: List[str]
    confidence_score: float
    timestamp: datetime
    reasoning_trace: List[str]


@dataclass
class TransparencyReport:
    """Comprehensive transparency report for agent execution."""
    execution_id: str
    query: str
    agent_name: str
    start_time: datetime
    end_time: datetime
    reasoning_steps: List[ReasoningStep]
    knowledge_sources: List[KnowledgeSource]
    validation_records: List[ValidationRecord]
    final_confidence: float
    transparency_score: float  # How transparent the process was
    audit_trail: List[str]


class TransparencyService:
    """Service for maintaining transparency in agent decision-making."""

    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)

        # In-memory storage (would be database in production)
        self.reasoning_steps: Dict[str, List[ReasoningStep]] = {}
        self.knowledge_sources: Dict[str, List[KnowledgeSource]] = {}
        self.validation_records: Dict[str, List[ValidationRecord]] = {}
        self.transparency_reports: Dict[str, TransparencyReport] = {}

        # Statistics
        self.stats = {
            "total_executions": 0,
            "average_transparency_score": 0.0,
            "source_reliability_distribution": {},
            "most_used_sources": {},
            "validation_success_rate": 0.0
        }

    def start_transparency_tracking(self, execution_id: str, query: str, agent_name: str) -> str:
        """Start tracking transparency for an agent execution."""
        self.reasoning_steps[execution_id] = []
        self.knowledge_sources[execution_id] = []
        self.validation_records[execution_id] = []

        # Initialize transparency report
        report = TransparencyReport(
            execution_id=execution_id,
            query=query,
            agent_name=agent_name,
            start_time=datetime.now(),
            end_time=datetime.now(),  # Will be updated
            reasoning_steps=[],
            knowledge_sources=[],
            validation_records=[],
            final_confidence=0.0,
            transparency_score=1.0,  # Start with perfect transparency
            audit_trail=[f"Started execution tracking for query: {query}"]
        )

        self.transparency_reports[execution_id] = report
        self.logger.info(f"Started transparency tracking for execution {execution_id}")

        return execution_id

    def record_reasoning_step(
        self,
        execution_id: str,
        step_type: str,
        description: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        confidence_score: float,
        sources_used: List[str],
        first_principles_applied: List[str],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a single reasoning step."""
        if execution_id not in self.reasoning_steps:
            self.logger.warning(f"Execution {execution_id} not found for reasoning step recording")
            return ""

        step_id = f"{execution_id}_step_{len(self.reasoning_steps[execution_id])}"

        step = ReasoningStep(
            step_id=step_id,
            agent_name=self.transparency_reports[execution_id].agent_name,
            timestamp=datetime.now(),
            step_type=step_type,
            description=description,
            inputs=inputs,
            outputs=outputs,
            confidence_score=confidence_score,
            sources_used=sources_used,
            first_principles_applied=first_principles_applied,
            processing_time=processing_time,
            metadata=metadata or {}
        )

        self.reasoning_steps[execution_id].append(step)

        # Update transparency report
        if execution_id in self.transparency_reports:
            self.transparency_reports[execution_id].reasoning_steps.append(step)
            self.transparency_reports[execution_id].audit_trail.append(
                f"Step {step_type}: {description} (confidence: {confidence_score:.2f})"
            )

        # Update transparency score based on step characteristics
        self._update_transparency_score(execution_id, step)

        return step_id

    def record_knowledge_source(
        self,
        execution_id: str,
        source_type: str,
        source_name: str,
        url: Optional[str] = None,
        content: Any = None,
        reliability_score: float = 0.8,
        domain: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a knowledge source used in reasoning."""
        if execution_id not in self.knowledge_sources:
            self.logger.warning(f"Execution {execution_id} not found for source recording")
            return ""

        # Create content hash for verification
        content_str = json.dumps(content, sort_keys=True) if content else ""
        content_hash = hashlib.md5(content_str.encode()).hexdigest()

        source_id = f"{execution_id}_source_{len(self.knowledge_sources[execution_id])}"

        source = KnowledgeSource(
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            url=url,
            timestamp=datetime.now(),
            content_hash=content_hash,
            reliability_score=reliability_score,
            domain=domain,
            metadata=metadata or {}
        )

        self.knowledge_sources[execution_id].append(source)

        # Update transparency report
        if execution_id in self.transparency_reports:
            self.transparency_reports[execution_id].knowledge_sources.append(source)
            self.transparency_reports[execution_id].audit_trail.append(
                f"Source used: {source_name} ({source_type}, reliability: {reliability_score:.2f})"
            )

        # Update statistics
        self._update_source_statistics(source)

        return source_id

    def record_validation(
        self,
        execution_id: str,
        claim: str,
        validation_type: str,
        validator_agent: str,
        validation_result: str,
        evidence_used: List[str],
        counter_evidence: List[str],
        confidence_score: float,
        reasoning_trace: List[str]
    ) -> str:
        """Record a validation of a scientific claim."""
        if execution_id not in self.validation_records:
            self.logger.warning(f"Execution {execution_id} not found for validation recording")
            return ""

        validation_id = f"{execution_id}_validation_{len(self.validation_records[execution_id])}"

        validation = ValidationRecord(
            validation_id=validation_id,
            claim=claim,
            validation_type=validation_type,
            validator_agent=validator_agent,
            validation_result=validation_result,
            evidence_used=evidence_used,
            counter_evidence=counter_evidence,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
            reasoning_trace=reasoning_trace
        )

        self.validation_records[execution_id].append(validation)

        # Update transparency report
        if execution_id in self.transparency_reports:
            self.transparency_reports[execution_id].validation_records.append(validation)
            self.transparency_reports[execution_id].audit_trail.append(
                f"Validation: {claim[:50]}... → {validation_result} (confidence: {confidence_score:.2f})"
            )

        # Update validation statistics
        self._update_validation_statistics(validation)

        return validation_id

    def complete_transparency_tracking(
        self,
        execution_id: str,
        final_result: AgentResult,
        final_confidence: float
    ) -> TransparencyReport:
        """Complete transparency tracking for an execution."""
        if execution_id not in self.transparency_reports:
            self.logger.error(f"Transparency report not found for execution {execution_id}")
            return None

        report = self.transparency_reports[execution_id]
        report.end_time = datetime.now()
        report.final_confidence = final_confidence

        # Calculate final transparency score
        report.transparency_score = self._calculate_final_transparency_score(execution_id)

        # Add final audit entry
        report.audit_trail.append(
            f"Execution completed: confidence {final_confidence:.2f}, "
            f"transparency {report.transparency_score:.2f}"
        )

        # Update global statistics
        self._update_global_statistics(report)

        self.logger.info(f"Completed transparency tracking for execution {execution_id}")
        return report

    def get_transparency_report(self, execution_id: str) -> Optional[TransparencyReport]:
        """Get transparency report for an execution."""
        return self.transparency_reports.get(execution_id)

    def get_execution_trace(self, execution_id: str) -> Dict[str, Any]:
        """Get complete execution trace including all transparency data."""
        if execution_id not in self.transparency_reports:
            return {"error": "Execution not found"}

        report = self.transparency_reports[execution_id]

        return {
            "execution_id": execution_id,
            "summary": {
                "query": report.query,
                "agent": report.agent_name,
                "duration": (report.end_time - report.start_time).total_seconds(),
                "final_confidence": report.final_confidence,
                "transparency_score": report.transparency_score,
                "steps_count": len(report.reasoning_steps),
                "sources_count": len(report.knowledge_sources),
                "validations_count": len(report.validation_records)
            },
            "reasoning_steps": [asdict(step) for step in report.reasoning_steps],
            "knowledge_sources": [asdict(source) for source in report.knowledge_sources],
            "validation_records": [asdict(validation) for validation in report.validation_records],
            "audit_trail": report.audit_trail
        }

    def validate_source_integrity(self, source_id: str, current_content: Any) -> Dict[str, Any]:
        """Validate that a knowledge source hasn't been tampered with."""
        # Find the source across all executions
        for execution_sources in self.knowledge_sources.values():
            for source in execution_sources:
                if source.source_id == source_id:
                    # Check content hash
                    current_content_str = json.dumps(current_content, sort_keys=True)
                    current_hash = hashlib.md5(current_content_str.encode()).hexdigest()

                    integrity_check = {
                        "source_id": source_id,
                        "original_hash": source.content_hash,
                        "current_hash": current_hash,
                        "integrity_maintained": source.content_hash == current_hash,
                        "timestamp_checked": datetime.now().isoformat(),
                        "age_hours": (datetime.now() - source.timestamp).total_seconds() / 3600
                    }

                    return integrity_check

        return {"error": "Source not found", "source_id": source_id}

    def get_source_reliability_report(self, source_name: str) -> Dict[str, Any]:
        """Get reliability report for a knowledge source."""
        reliability_data = {
            "source_name": source_name,
            "usage_count": 0,
            "average_reliability": 0.0,
            "usage_by_domain": {},
            "recent_usage": [],
            "reliability_trend": []
        }

        # Aggregate data from all executions
        reliabilities = []
        for execution_sources in self.knowledge_sources.values():
            for source in execution_sources:
                if source.source_name == source_name:
                    reliability_data["usage_count"] += 1
                    reliabilities.append(source.reliability_score)

                    # Track by domain
                    domain = source.domain
                    if domain not in reliability_data["usage_by_domain"]:
                        reliability_data["usage_by_domain"][domain] = 0
                    reliability_data["usage_by_domain"][domain] += 1

        if reliabilities:
            reliability_data["average_reliability"] = sum(reliabilities) / len(reliabilities)

        return reliability_data

    def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive audit report for a date range."""
        audit_report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "executions": {
                "total": 0,
                "by_agent": {},
                "by_domain": {},
                "average_confidence": 0.0,
                "average_transparency": 0.0
            },
            "sources": {
                "total_used": 0,
                "by_type": {},
                "reliability_distribution": {},
                "most_reliable": []
            },
            "validations": {
                "total": 0,
                "success_rate": 0.0,
                "by_type": {},
                "common_claims": []
            },
            "anomalies": []
        }

        # Filter reports by date range
        relevant_reports = [
            report for report in self.transparency_reports.values()
            if start_date <= report.start_time <= end_date
        ]

        audit_report["executions"]["total"] = len(relevant_reports)

        # Analyze executions
        confidences = []
        transparencies = []
        agent_counts = {}
        domain_counts = {}

        for report in relevant_reports:
            confidences.append(report.final_confidence)
            transparencies.append(report.transparency_score)

            # Count by agent
            agent = report.agent_name
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

            # Infer domain from agent name (simplified)
            if "physics" in agent:
                domain_counts["physics"] = domain_counts.get("physics", 0) + 1
            elif "chemistry" in agent:
                domain_counts["chemistry"] = domain_counts.get("chemistry", 0) + 1
            elif "mathematics" in agent:
                domain_counts["mathematics"] = domain_counts.get("mathematics", 0) + 1

        audit_report["executions"]["by_agent"] = agent_counts
        audit_report["executions"]["by_domain"] = domain_counts

        if confidences:
            audit_report["executions"]["average_confidence"] = sum(confidences) / len(confidences)
        if transparencies:
            audit_report["executions"]["average_transparency"] = sum(transparencies) / len(transparencies)

        return audit_report

    def _update_transparency_score(self, execution_id: str, step: ReasoningStep):
        """Update transparency score based on reasoning step characteristics."""
        if execution_id not in self.transparency_reports:
            return

        report = self.transparency_reports[execution_id]

        # Penalize low confidence steps
        if step.confidence_score < 0.5:
            report.transparency_score *= 0.95

        # Penalize steps with unclear reasoning
        if not step.description or len(step.description.strip()) < 10:
            report.transparency_score *= 0.98

        # Penalize steps without sources
        if not step.sources_used:
            report.transparency_score *= 0.97

        # Penalize steps without first principles
        if not step.first_principles_applied:
            report.transparency_score *= 0.96

        # Ensure transparency score doesn't go below 0.1
        report.transparency_score = max(report.transparency_score, 0.1)

    def _update_source_statistics(self, source: KnowledgeSource):
        """Update global source statistics."""
        # Update reliability distribution
        reliability_bucket = f"{int(source.reliability_score * 10) / 10:.1f}"
        self.stats["source_reliability_distribution"][reliability_bucket] = \
            self.stats["source_reliability_distribution"].get(reliability_bucket, 0) + 1

        # Update most used sources
        self.stats["most_used_sources"][source.source_name] = \
            self.stats["most_used_sources"].get(source.source_name, 0) + 1

    def _update_validation_statistics(self, validation: ValidationRecord):
        """Update validation statistics."""
        # Simple success rate tracking (simplified - would be more sophisticated)
        if validation.validation_result in ["supported", "refuted"]:
            # Consider it a successful validation if we reached a conclusion
            self.stats["validation_success_rate"] = (
                self.stats["validation_success_rate"] * 0.9 + 1.0 * 0.1
            )
        else:
            self.stats["validation_success_rate"] = (
                self.stats["validation_success_rate"] * 0.9 + 0.0 * 0.1
            )

    def _calculate_final_transparency_score(self, execution_id: str) -> float:
        """Calculate final transparency score for an execution."""
        if execution_id not in self.transparency_reports:
            return 0.0

        report = self.transparency_reports[execution_id]

        # Base score from individual steps
        base_score = report.transparency_score

        # Bonus for comprehensive audit trail
        audit_bonus = min(len(report.audit_trail) * 0.01, 0.2)  # Max 0.2 bonus

        # Bonus for multiple sources
        source_bonus = min(len(report.knowledge_sources) * 0.05, 0.3)  # Max 0.3 bonus

        # Bonus for validations
        validation_bonus = min(len(report.validation_records) * 0.1, 0.4)  # Max 0.4 bonus

        # Penalty for short executions (might indicate insufficient reasoning)
        duration_penalty = max(0, (300 - (report.end_time - report.start_time).total_seconds()) * 0.001)  # Max 0.3 penalty

        final_score = base_score + audit_bonus + source_bonus + validation_bonus - duration_penalty
        return max(0.0, min(1.0, final_score))  # Clamp to [0, 1]

    def _update_global_statistics(self, report: TransparencyReport):
        """Update global transparency statistics."""
        self.stats["total_executions"] += 1

        # Update average transparency score
        current_avg = self.stats["average_transparency_score"]
        new_avg = (current_avg * (self.stats["total_executions"] - 1) + report.transparency_score) / self.stats["total_executions"]
        self.stats["average_transparency_score"] = new_avg

    def cleanup_old_data(self):
        """Clean up old transparency data beyond retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        # Clean up reasoning steps
        executions_to_remove = []
        for execution_id, steps in self.reasoning_steps.items():
            if steps and steps[0].timestamp < cutoff_date:
                executions_to_remove.append(execution_id)

        # Remove old data
        for execution_id in executions_to_remove:
            self.reasoning_steps.pop(execution_id, None)
            self.knowledge_sources.pop(execution_id, None)
            self.validation_records.pop(execution_id, None)
            self.transparency_reports.pop(execution_id, None)

        if executions_to_remove:
            self.logger.info(f"Cleaned up {len(executions_to_remove)} old transparency records")

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get summary of transparency statistics."""
        return {
            "total_executions_tracked": self.stats["total_executions"],
            "average_transparency_score": round(self.stats["average_transparency_score"], 3),
            "validation_success_rate": round(self.stats["validation_success_rate"], 3),
            "most_used_sources": dict(sorted(
                self.stats["most_used_sources"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),  # Top 10 sources
            "source_reliability_distribution": self.stats["source_reliability_distribution"],
            "data_retention_days": self.retention_days,
            "last_cleanup": datetime.now().isoformat()  # Would track actual cleanup time
        }
