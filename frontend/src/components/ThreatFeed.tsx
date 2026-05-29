"use client";

import { AlertTriangle, Shield, Key, Building2, FileWarning, Search, CheckCircle, Bell } from "lucide-react";
import type { SSEEvent } from "@/lib/api";

interface ThreatFeedProps {
  events: SSEEvent[];
}

const AGENT_LABELS: Record<string, string> = {
  orchestrator: "Orchestrator",
  discovery: "CVE & Advisory Scanner",
  credential_leak: "Credential Leak Scanner",
  vendor_risk: "Vendor Risk Assessor",
  correlation: "Environment Correlation",
  risk_assessment: "Risk Scoring",
  remediation: "Remediation Planner",
  notify: "Notification Dispatch",
  should_remediate: "Severity Check",
};

const AGENT_ICONS: Record<string, typeof AlertTriangle> = {
  discovery: AlertTriangle,
  credential_leak: Key,
  vendor_risk: Building2,
  correlation: Shield,
  risk_assessment: FileWarning,
  remediation: FileWarning,
  orchestrator: Search,
  notify: Bell,
  should_remediate: Shield,
};

const AGENT_START_MSG: Record<string, string> = {
  orchestrator: "Loading environment inventory...",
  discovery: "Scanning web for CVEs, advisories, and breaches...",
  credential_leak: "Searching paste sites and code repos for leaked credentials...",
  vendor_risk: "Assessing third-party vendor security posture...",
  correlation: "Matching threats against your infrastructure...",
  risk_assessment: "Calculating blast radius and severity scores...",
  remediation: "Generating fix commands and upgrade paths...",
  notify: "Sending Slack alerts and creating Jira tickets...",
  should_remediate: "Evaluating severity thresholds...",
};

const AGENT_DONE_MSG: Record<string, string> = {
  orchestrator: "Environment loaded",
  discovery: "Web scan complete",
  credential_leak: "Credential scan complete",
  vendor_risk: "Vendor assessment complete",
  correlation: "Correlation complete",
  risk_assessment: "Risk scoring complete",
  remediation: "Remediation plans generated",
  notify: "Notifications sent",
  should_remediate: "Severity evaluated",
};

export default function ThreatFeed({ events }: ThreatFeedProps) {
  const filteredEvents = events.filter(
    (e) => (e.type === "agent_start" || e.type === "agent_complete") && e.agent
  );

  return (
    <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Agent Activity
      </h2>
      <div className="space-y-1.5 max-h-[400px] overflow-y-auto">
        {filteredEvents.length === 0 && (
          <p className="text-sm text-gray-600 text-center py-6">
            Waiting for investigation to start...
          </p>
        )}
        {filteredEvents.map((event, i) => {
          const agentName = event.agent || "";
          const Icon = AGENT_ICONS[agentName] || Shield;
          const label = AGENT_LABELS[agentName] || agentName;
          const isStart = event.type === "agent_start";
          const message = isStart
            ? AGENT_START_MSG[agentName] || "Processing..."
            : AGENT_DONE_MSG[agentName] || "Done";

          return (
            <div
              key={i}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg ${
                isStart ? "bg-blue-500/5 border border-blue-500/10" : "bg-[#1a1a1a] border border-[#262626]"
              }`}
            >
              {isStart ? (
                <Icon className="w-3.5 h-3.5 text-blue-400 shrink-0 animate-pulse" />
              ) : (
                <CheckCircle className="w-3.5 h-3.5 text-green-400 shrink-0" />
              )}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-medium ${isStart ? "text-blue-300" : "text-green-300"}`}>
                    {label}
                  </span>
                  {event.threats_found !== undefined && event.threats_found > 0 && (
                    <span className="text-[10px] px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded font-medium">
                      +{event.threats_found}
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-gray-500">{message}</p>
              </div>
              {event.timestamp && (
                <span className="text-[10px] text-gray-600 shrink-0">
                  {new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
