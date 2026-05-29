from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatType(str, Enum):
    CVE = "cve"
    ADVISORY = "advisory"
    CREDENTIAL_LEAK = "credential_leak"
    BRAND_IMPERSONATION = "brand_impersonation"
    VENDOR_BREACH = "vendor_breach"
    REGULATORY_CHANGE = "regulatory_change"


class InvestigationRequest(BaseModel):
    target: str = Field(description="Company or organization name")
    domain: Optional[str] = Field(default=None, description="Primary domain")
    industry: Optional[str] = Field(default="technology", description="Industry vertical")


class DiscoveredThreat(BaseModel):
    id: str = Field(default_factory=lambda: "")
    threat_type: ThreatType
    title: str
    description: str
    severity: Severity
    source_url: str
    cve_id: Optional[str] = None
    affected_versions: list[str] = Field(default_factory=list)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now())
    raw_data: dict = Field(default_factory=dict)


class CorrelatedThreat(BaseModel):
    threat: DiscoveredThreat
    affected_resources: list[dict] = Field(default_factory=list)
    environment_match: bool = False
    match_details: str = ""


class RiskScore(BaseModel):
    threat_id: str
    score: int = Field(ge=0, le=100)
    blast_radius: str = ""
    exploitability: str = ""
    is_internet_facing: bool = False
    existing_mitigations: list[str] = Field(default_factory=list)
    reasoning: str = ""


class RemediationPlan(BaseModel):
    threat_id: str
    title: str
    priority: Severity
    steps: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    terraform_changes: Optional[str] = None
    estimated_effort: str = ""


class CredentialLeak(BaseModel):
    source_url: str
    leak_type: str
    affected_accounts: list[str] = Field(default_factory=list)
    severity: Severity
    discovered_at: datetime = Field(default_factory=lambda: datetime.now())
    recommended_action: str = ""


class VendorRisk(BaseModel):
    vendor_name: str
    risk_score: int = Field(ge=0, le=100)
    incidents: list[dict] = Field(default_factory=list)
    compliance_issues: list[str] = Field(default_factory=list)
    last_assessed: datetime = Field(default_factory=lambda: datetime.now())


class ThreatReport(BaseModel):
    investigation_id: str
    target: str
    total_threats: int = 0
    critical_count: int = 0
    high_count: int = 0
    threats: list[CorrelatedThreat] = Field(default_factory=list)
    risk_scores: list[RiskScore] = Field(default_factory=list)
    remediation_plans: list[RemediationPlan] = Field(default_factory=list)
    credential_leaks: list[CredentialLeak] = Field(default_factory=list)
    vendor_risks: list[VendorRisk] = Field(default_factory=list)


class AgentTraceEntry(BaseModel):
    agent: str
    action: str
    detail: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
