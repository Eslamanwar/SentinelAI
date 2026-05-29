"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Shield, ArrowLeft, Activity, AlertTriangle, Key, Building2, FileText } from "lucide-react";
import Link from "next/link";
import ThreatFeed from "@/components/ThreatFeed";
import AgentTrace from "@/components/AgentTrace";
import RiskMatrix from "@/components/RiskMatrix";
import RemediationCard from "@/components/RemediationCard";
import { startInvestigation, parseSSEStream, type SSEEvent } from "@/lib/api";

interface AgentStatus {
  name: string;
  label: string;
  status: "pending" | "running" | "complete";
}

const INITIAL_AGENTS: AgentStatus[] = [
  { name: "orchestrator", label: "Orchestrator", status: "pending" },
  { name: "discovery", label: "Discovery (CVE/Advisory)", status: "pending" },
  { name: "credential_leak", label: "Credential Leak Scanner", status: "pending" },
  { name: "vendor_risk", label: "Vendor Risk Assessment", status: "pending" },
  { name: "correlation", label: "Environment Correlation", status: "pending" },
  { name: "risk_assessment", label: "Risk Scoring", status: "pending" },
  { name: "remediation", label: "Remediation Planning", status: "pending" },
  { name: "notify", label: "Slack / Jira Notification", status: "pending" },
];

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-500/20 text-red-400 border-red-500/30",
  high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  low: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  info: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

function DashboardContent() {
  const searchParams = useSearchParams();
  const target = searchParams.get("target") || "";
  const domain = searchParams.get("domain") || "";
  const industry = searchParams.get("industry") || "technology";

  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [agents, setAgents] = useState<AgentStatus[]>(INITIAL_AGENTS);
  const [threats, setThreats] = useState<any[]>([]);
  const [credentialLeaks, setCredentialLeaks] = useState<any[]>([]);
  const [vendorRisks, setVendorRisks] = useState<any[]>([]);
  const [correlatedThreats, setCorrelatedThreats] = useState<any[]>([]);
  const [riskScores, setRiskScores] = useState<any[]>([]);
  const [remediationPlans, setRemediationPlans] = useState<any[]>([]);
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const [threatCount, setThreatCount] = useState(0);

  const updateAgentStatus = useCallback((name: string, newStatus: "running" | "complete") => {
    setAgents((prev) =>
      prev.map((a) => (a.name === name ? { ...a, status: newStatus } : a))
    );
  }, []);

  useEffect(() => {
    if (!target) return;

    let cancelled = false;

    async function run() {
      setStatus("running");
      try {
        const response = await startInvestigation(target, domain, industry);

        for await (const event of parseSSEStream(response)) {
          if (cancelled) break;

          if (event.type === "agent_start" && event.agent) {
            updateAgentStatus(event.agent, "running");
            setEvents((prev) => [...prev, event]);
          }
          else if (event.type === "agent_complete" && event.agent) {
            updateAgentStatus(event.agent, "complete");
            if (event.threats_found) {
              setThreatCount((prev) => prev + event.threats_found!);
            }
            setEvents((prev) => [...prev, event]);
          }
          else if (event.type === "threats") {
            setThreats((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "credential_leaks") {
            setCredentialLeaks((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "vendor_risks") {
            setVendorRisks((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "correlated_threats") {
            setCorrelatedThreats((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "risk_scores") {
            setRiskScores((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "remediation_plans") {
            setRemediationPlans((prev) => [...prev, ...(event as any).data]);
          }
          else if (event.type === "complete") {
            setStatus("complete");
          }
          else if (event.type === "error") {
            setStatus("error");
            setEvents((prev) => [...prev, event]);
          }
        }
      } catch {
        if (!cancelled) setStatus("error");
      }
    }

    run();
    return () => { cancelled = true; };
  }, [target, domain, industry, updateAgentStatus]);

  const riskItems = riskScores.map((r: any) => ({
    label: threats.find((t: any) => t.id === r.threat_id)?.title || r.threat_id || "Unknown",
    score: r.score || 0,
    category: r.exploitability || "unknown",
  }));

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-[#262626] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-500 hover:text-gray-300">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <Shield className="w-6 h-6 text-blue-500" />
            <div>
              <h1 className="font-semibold">Investigating: {target}</h1>
              <p className="text-xs text-gray-500">
                {domain && `${domain} · `}{industry}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
              status === "running"
                ? "bg-blue-500/20 text-blue-400"
                : status === "complete"
                ? "bg-green-500/20 text-green-400"
                : status === "error"
                ? "bg-red-500/20 text-red-400"
                : "bg-gray-500/20 text-gray-400"
            }`}>
              {status === "running" && <Activity className="w-3 h-3 animate-pulse" />}
              {status === "running" ? "Investigating..." : status === "complete" ? "Complete" : status === "error" ? "Error" : "Starting..."}
            </div>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Left Column: Agent Pipeline + Stats */}
        <div className="col-span-3 space-y-6">
          <AgentTrace agents={agents} />

          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-red-400">{threats.length}</p>
              <p className="text-xs text-gray-500">Threats</p>
            </div>
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-orange-400">{credentialLeaks.length}</p>
              <p className="text-xs text-gray-500">Cred Leaks</p>
            </div>
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-purple-400">{vendorRisks.length}</p>
              <p className="text-xs text-gray-500">Vendor Risks</p>
            </div>
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-blue-400">
                {agents.filter((a) => a.status === "complete").length}/{agents.length}
              </p>
              <p className="text-xs text-gray-500">Agents Done</p>
            </div>
          </div>
        </div>

        {/* Center Column: Threats + Remediation */}
        <div className="col-span-5 space-y-6">
          {/* Discovered Threats */}
          <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Discovered Threats ({threats.length})
            </h2>
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {threats.length === 0 && status === "running" && (
                <p className="text-sm text-gray-600 text-center py-8">Scanning for threats...</p>
              )}
              {threats.length === 0 && status === "complete" && (
                <p className="text-sm text-green-400 text-center py-8">No threats found</p>
              )}
              {threats.map((threat: any, i: number) => (
                <div key={i} className="p-3 bg-[#1a1a1a] rounded-lg border border-[#262626]">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-sm font-medium text-gray-200">{threat.title}</h3>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border shrink-0 ${SEVERITY_COLORS[threat.severity] || SEVERITY_COLORS.info}`}>
                      {threat.severity?.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{threat.description}</p>
                  <div className="flex items-center gap-3 mt-2">
                    {threat.cve_id && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded">{threat.cve_id}</span>
                    )}
                    <span className="text-[10px] text-gray-600">{threat.threat_type}</span>
                    {threat.source_url && (
                      <a href={threat.source_url} target="_blank" rel="noopener" className="text-[10px] text-blue-500 hover:underline truncate max-w-[150px]">
                        source
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Credential Leaks */}
          {credentialLeaks.length > 0 && (
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Key className="w-4 h-4" />
                Credential Leaks ({credentialLeaks.length})
              </h2>
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {credentialLeaks.map((leak: any, i: number) => (
                  <div key={i} className="p-3 bg-[#1a1a1a] rounded-lg border border-[#262626]">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-200">{leak.leak_type}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full border ${SEVERITY_COLORS[leak.severity] || SEVERITY_COLORS.info}`}>
                        {leak.severity?.toUpperCase()}
                      </span>
                    </div>
                    {leak.source_url && (
                      <a href={leak.source_url} target="_blank" rel="noopener" className="text-[10px] text-blue-500 hover:underline block mt-1 truncate">{leak.source_url}</a>
                    )}
                    <p className="text-xs text-gray-500 mt-1">{leak.recommended_action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Remediation Plans */}
          {remediationPlans.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Remediation Plans ({remediationPlans.length})
              </h2>
              {remediationPlans.map((plan: any, i: number) => (
                <RemediationCard key={i} plan={plan} />
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Risk Scores + Vendor Risks */}
        <div className="col-span-4 space-y-6">
          <RiskMatrix items={riskItems} />

          {/* Vendor Risks */}
          {vendorRisks.length > 0 && (
            <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Building2 className="w-4 h-4" />
                Vendor Risk ({vendorRisks.length})
              </h2>
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {vendorRisks.map((vendor: any, i: number) => (
                  <div key={i} className="p-3 bg-[#1a1a1a] rounded-lg border border-[#262626]">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-200">{vendor.vendor_name}</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                        vendor.risk_score >= 80 ? "bg-red-500/20 text-red-400"
                        : vendor.risk_score >= 60 ? "bg-orange-500/20 text-orange-400"
                        : vendor.risk_score >= 40 ? "bg-yellow-500/20 text-yellow-400"
                        : "bg-green-500/20 text-green-400"
                      }`}>
                        {vendor.risk_score}/100
                      </span>
                    </div>
                    {vendor.recommendation && (
                      <p className="text-xs text-gray-500 mt-1">{vendor.recommendation}</p>
                    )}
                    {vendor.incidents?.length > 0 && (
                      <div className="mt-1">
                        {vendor.incidents.slice(0, 2).map((inc: any, j: number) => (
                          <span key={j} className="text-[10px] text-orange-400 mr-2">{inc.title || inc}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Agent Trace / Live Feed */}
          <ThreatFeed events={events} />
        </div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
