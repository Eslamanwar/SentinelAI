"use client";

import { CheckCircle, Circle, Loader2 } from "lucide-react";

interface AgentStatus {
  name: string;
  label: string;
  status: "pending" | "running" | "complete";
}

interface AgentTraceProps {
  agents: AgentStatus[];
}

export default function AgentTrace({ agents }: AgentTraceProps) {
  return (
    <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Agent Pipeline
      </h2>
      <div className="space-y-1">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
              agent.status === "running"
                ? "bg-blue-500/10 border border-blue-500/20"
                : agent.status === "complete"
                ? "bg-green-500/5"
                : "opacity-50"
            }`}
          >
            {agent.status === "pending" && (
              <Circle className="w-4 h-4 text-gray-600" />
            )}
            {agent.status === "running" && (
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            )}
            {agent.status === "complete" && (
              <CheckCircle className="w-4 h-4 text-green-400" />
            )}
            <span
              className={`text-sm ${
                agent.status === "running"
                  ? "text-blue-300 font-medium"
                  : agent.status === "complete"
                  ? "text-green-300"
                  : "text-gray-500"
              }`}
            >
              {agent.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
