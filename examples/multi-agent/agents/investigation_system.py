"""
Multi-Agent Incident Investigation System

This module implements a multi-agent system for autonomous incident investigation.
Agents collaborate to triage, correlate, and analyze incidents across distributed systems.

Agent Types:
- Triage Agent: First responder, classifies severity and routes to specialists
- Correlation Agent: Finds relationships between symptoms across services
- Root Cause Agent: Deep dives to find root causes
- Remediation Agent: Suggests fixes based on historical data
- Learning Agent: Improves investigation patterns over time
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Roles that agents can have in the investigation system."""
    TRIAGE = "triage"
    CORRELATION = "correlation"
    ROOT_CAUSE = "root_cause"
    REMEDIATION = "remediation"
    LEARNING = "learning"
    ORCHESTRATOR = "orchestrator"


class Severity(Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """
    Represents a finding from an agent's investigation.
    """
    agent_role: AgentRole
    timestamp: datetime
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    related_findings: List[str] = field(default_factory=list)
    actions_suggested: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "agent_role": self.agent_role.value,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "related_findings": self.related_findings,
            "actions_suggested": self.actions_suggested,
        }


@dataclass
class InvestigationContext:
    """
    Context shared between agents during an investigation.
    """
    incident_id: str
    correlation_id: Optional[str] = None
    severity: Optional[Severity] = None
    affected_services: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_finding(self, finding: Finding):
        """Add a finding to the investigation context."""
        self.findings.append(finding)
        logger.info(
            f"Finding added by {finding.agent_role.value}: {finding.title} "
            f"(confidence: {finding.confidence:.2f})"
        )
    
    def get_findings_by_role(self, role: AgentRole) -> List[Finding]:
        """Get all findings from a specific agent role."""
        return [f for f in self.findings if f.agent_role == role]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "incident_id": self.incident_id,
            "correlation_id": self.correlation_id,
            "severity": self.severity.value if self.severity else None,
            "affected_services": self.affected_services,
            "symptoms": self.symptoms,
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
        }


class Agent(ABC):
    """
    Base class for investigation agents.
    
    All agents must implement the investigate method.
    """
    
    def __init__(self, role: AgentRole, mcp_client=None):
        """
        Initialize the agent.
        
        Args:
            role: The role this agent performs
            mcp_client: Client for querying observability data
        """
        self.role = role
        self.mcp_client = mcp_client
        self.logger = logging.getLogger(f"agent.{role.value}")
    
    @abstractmethod
    async def investigate(self, context: InvestigationContext) -> List[Finding]:
        """
        Perform investigation based on the context.
        
        Args:
            context: Investigation context with incident details
            
        Returns:
            List of findings from this agent's investigation
        """
        pass
    
    def log_investigation_start(self, context: InvestigationContext):
        """Log the start of investigation."""
        self.logger.info(
            f"Starting {self.role.value} investigation for incident {context.incident_id}"
        )
    
    def log_investigation_complete(self, findings: List[Finding]):
        """Log the completion of investigation."""
        self.logger.info(
            f"Completed {self.role.value} investigation. "
            f"Found {len(findings)} findings."
        )


class TriageAgent(Agent):
    """
    First responder agent that classifies severity and routes to specialists.
    
    Responsibilities:
    - Classify incident severity
    - Identify affected services
    - Extract initial symptoms
    - Route to appropriate specialists
    """
    
    def __init__(self, mcp_client=None):
        super().__init__(AgentRole.TRIAGE, mcp_client)
    
    async def investigate(self, context: InvestigationContext) -> List[Finding]:
        """Perform triage investigation."""
        self.log_investigation_start(context)
        findings = []
        
        # Classify severity based on symptoms
        severity = await self._classify_severity(context)
        context.severity = severity
        
        findings.append(Finding(
            agent_role=self.role,
            timestamp=datetime.utcnow(),
            title=f"Incident classified as {severity.value}",
            description=f"Based on symptoms: {', '.join(context.symptoms)}",
            confidence=0.85,
            evidence=[{"symptoms": context.symptoms}],
            actions_suggested=[
                f"Escalate to {severity.value} priority",
                "Assign to correlation and root cause agents",
            ],
        ))
        
        # Identify affected services
        affected_services = await self._identify_affected_services(context)
        context.affected_services = affected_services
        
        if affected_services:
            findings.append(Finding(
                agent_role=self.role,
                timestamp=datetime.utcnow(),
                title=f"Identified {len(affected_services)} affected services",
                description=f"Services: {', '.join(affected_services)}",
                confidence=0.90,
                evidence=[{"services": affected_services}],
                actions_suggested=[
                    "Deep dive into affected services",
                    "Check service dependencies",
                ],
            ))
        
        self.log_investigation_complete(findings)
        return findings
    
    async def _classify_severity(self, context: InvestigationContext) -> Severity:
        """Classify incident severity based on symptoms."""
        # Simple rule-based classification (in production, use ML)
        symptoms = set(context.symptoms)
        
        if any(s in symptoms for s in ["outage", "data_loss", "security_breach"]):
            return Severity.CRITICAL
        elif any(s in symptoms for s in ["error_rate_spike", "high_latency", "timeout"]):
            return Severity.HIGH
        elif any(s in symptoms for s in ["degraded_performance", "warning_increase"]):
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    async def _identify_affected_services(
        self, context: InvestigationContext
    ) -> List[str]:
        """Identify affected services from initial symptoms."""
        # In a real implementation, query MCP for error logs
        # For this example, return mock data
        return ["payment-service", "auth-service"]


class CorrelationAgent(Agent):
    """
    Agent that finds relationships between symptoms across services.
    
    Responsibilities:
    - Correlate logs, traces, and metrics
    - Identify cascading failures
    - Map service dependencies
    - Find temporal patterns
    """
    
    def __init__(self, mcp_client=None):
        super().__init__(AgentRole.CORRELATION, mcp_client)
    
    async def investigate(self, context: InvestigationContext) -> List[Finding]:
        """Perform correlation investigation."""
        self.log_investigation_start(context)
        findings = []
        
        # Find correlated telemetry
        if context.correlation_id:
            findings.append(Finding(
                agent_role=self.role,
                timestamp=datetime.utcnow(),
                title="Found correlated telemetry across services",
                description=(
                    "Discovered traces, logs, and metrics related to the incident"
                ),
                confidence=0.95,
                evidence=[{
                    "correlation_id": context.correlation_id,
                    "trace_count": 15,
                    "log_count": 42,
                    "metric_count": 8,
                }],
                actions_suggested=[
                    "Analyze trace spans for bottlenecks",
                    "Review error logs for root cause",
                ],
            ))
        
        # Identify cascading failures
        if len(context.affected_services) >= 2:
            findings.append(Finding(
                agent_role=self.role,
                timestamp=datetime.utcnow(),
                title="Potential cascading failure detected",
                description=(
                    f"Failure propagated from {context.affected_services[0]} "
                    f"to downstream services"
                ),
                confidence=0.75,
                evidence=[{
                    "pattern": "temporal_correlation",
                    "services": context.affected_services,
                }],
                actions_suggested=[
                    f"Investigate {context.affected_services[0]} as potential root cause",
                    "Review service dependency graph",
                ],
            ))
        
        self.log_investigation_complete(findings)
        return findings


class RootCauseAgent(Agent):
    """
    Agent that performs deep dive to find root causes.
    
    Responsibilities:
    - Analyze trace spans for bottlenecks
    - Identify error patterns
    - Correlate with infrastructure metrics
    - Generate root cause hypotheses
    """
    
    def __init__(self, mcp_client=None):
        super().__init__(AgentRole.ROOT_CAUSE, mcp_client)
    
    async def investigate(self, context: InvestigationContext) -> List[Finding]:
        """Perform root cause investigation."""
        self.log_investigation_start(context)
        findings = []
        
        # Analyze error patterns
        findings.append(Finding(
            agent_role=self.role,
            timestamp=datetime.utcnow(),
            title="Error pattern identified in auth-service",
            description="Database connection pool exhausted",
            confidence=0.90,
            evidence=[{
                "error_message": "PoolExhaustedError: All 50 connections in use",
                "occurrence_count": 127,
                "time_window": "last_30m",
            }],
            actions_suggested=[
                "Increase database connection pool size",
                "Check for connection leaks",
            ],
        ))
        
        # Check infrastructure metrics
        findings.append(Finding(
            agent_role=self.role,
            timestamp=datetime.utcnow(),
            title="Infrastructure issue: high database connection usage",
            description="Database connections at capacity",
            confidence=0.85,
            evidence=[{
                "metric": "db_connections_active",
                "value": 50,
                "threshold": 50,
            }],
            actions_suggested=[
                "Scale database connection pool",
                "Investigate connection leak",
            ],
        ))
        
        # Generate root cause hypothesis
        hypothesis = Finding(
            agent_role=self.role,
            timestamp=datetime.utcnow(),
            title="Root cause hypothesis: Database connection pool exhaustion",
            description=(
                "auth-service database connection pool exhausted, causing timeouts "
                "that propagated to payment-service"
            ),
            confidence=0.88,
            evidence=[f.to_dict() for f in findings],
            related_findings=[f.title for f in findings],
            actions_suggested=[
                "Verify hypothesis with additional investigation",
                "Proceed with remediation",
            ],
        )
        findings.append(hypothesis)
        
        self.log_investigation_complete(findings)
        return findings


class RemediationAgent(Agent):
    """
    Agent that suggests remediation actions.
    
    Responsibilities:
    - Suggest fixes based on root cause
    - Provide runbook links
    - Estimate impact of remediation
    - Learn from past incidents
    """
    
    def __init__(self, mcp_client=None):
        super().__init__(AgentRole.REMEDIATION, mcp_client)
    
    async def investigate(self, context: InvestigationContext) -> List[Finding]:
        """Provide remediation suggestions."""
        self.log_investigation_start(context)
        findings = []
        
        # Get root cause findings
        rca_findings = context.get_findings_by_role(AgentRole.ROOT_CAUSE)
        
        for rca_finding in rca_findings:
            if rca_finding.confidence > 0.80 and "hypothesis" in rca_finding.title.lower():
                findings.append(Finding(
                    agent_role=self.role,
                    timestamp=datetime.utcnow(),
                    title="Remediation: Increase database connection pool",
                    description=(
                        "Immediate: Increase pool size from 50 to 100. "
                        "Long-term: Implement connection pooling monitoring."
                    ),
                    confidence=0.85,
                    evidence=[{
                        "runbook": "https://wiki.example.com/runbooks/db-connections",
                        "estimated_time": "5 minutes",
                        "risk_level": "low",
                    }],
                    related_findings=[rca_finding.title],
                    actions_suggested=[
                        "Update auth-service configuration: pool_size=100",
                        "Rolling restart auth-service pods",
                        "Monitor connection pool metrics",
                        "Set up alerting for pool usage >80%",
                    ],
                ))
        
        self.log_investigation_complete(findings)
        return findings


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    async def main():
        # Create investigation context
        context = InvestigationContext(
            incident_id="INC-2025-1113-001",
            correlation_id="e1f2a3b4c5d6789012345678901234cd",
            symptoms=["error_rate_spike", "high_latency", "timeout"],
        )
        
        # Create agents
        triage = TriageAgent()
        correlation = CorrelationAgent()
        root_cause = RootCauseAgent()
        remediation = RemediationAgent()
        
        # Run investigation
        print("\n" + "="*60)
        print("Multi-Agent Incident Investigation System")
        print("="*60 + "\n")
        
        # Triage
        print("Phase 1: Triage")
        print("-" * 60)
        triage_findings = await triage.investigate(context)
        for finding in triage_findings:
            context.add_finding(finding)
        print()
        
        # Correlation
        print("Phase 2: Correlation")
        print("-" * 60)
        correlation_findings = await correlation.investigate(context)
        for finding in correlation_findings:
            context.add_finding(finding)
        print()
        
        # Root Cause Analysis
        print("Phase 3: Root Cause Analysis")
        print("-" * 60)
        rca_findings = await root_cause.investigate(context)
        for finding in rca_findings:
            context.add_finding(finding)
        print()
        
        # Remediation
        print("Phase 4: Remediation")
        print("-" * 60)
        remediation_findings = await remediation.investigate(context)
        for finding in remediation_findings:
            context.add_finding(finding)
        print()
        
        # Print results
        print("\n" + "="*60)
        print("Investigation Complete - Summary")
        print("="*60 + "\n")
        
        print(f"Incident ID: {context.incident_id}")
        print(f"Severity: {context.severity.value if context.severity else 'Unknown'}")
        print(f"Affected Services: {', '.join(context.affected_services)}")
        print(f"Total Findings: {len(context.findings)}")
        print()
        
        # Print high-confidence findings
        print("High-Confidence Findings:")
        print("-" * 60)
        high_conf = [f for f in context.findings if f.confidence >= 0.85]
        for i, finding in enumerate(high_conf, 1):
            print(f"\n{i}. {finding.title}")
            print(f"   Agent: {finding.agent_role.value}")
            print(f"   Confidence: {finding.confidence:.2f}")
            print(f"   Description: {finding.description}")
            if finding.actions_suggested:
                print(f"   Actions:")
                for action in finding.actions_suggested:
                    print(f"     - {action}")
        
        print("\n" + "="*60)
        
        # Export full results
        with open("/tmp/investigation_results.json", "w") as f:
            json.dump(context.to_dict(), f, indent=2, default=str)
        
        print("\nFull results exported to /tmp/investigation_results.json")
    
    asyncio.run(main())
