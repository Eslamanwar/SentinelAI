"use client";

import { useState } from "react";
import { Copy, Check, Terminal } from "lucide-react";

interface RemediationPlan {
  title: string;
  priority: string;
  steps: string[];
  commands: string[];
  estimated_effort: string;
}

interface RemediationCardProps {
  plan: RemediationPlan;
}

export default function RemediationCard({ plan }: RemediationCardProps) {
  const [copied, setCopied] = useState<number | null>(null);

  const copyCommand = (cmd: string, index: number) => {
    navigator.clipboard.writeText(cmd);
    setCopied(index);
    setTimeout(() => setCopied(null), 2000);
  };

  const priorityColors: Record<string, string> = {
    critical: "border-red-500/30 bg-red-500/5",
    high: "border-orange-500/30 bg-orange-500/5",
    medium: "border-yellow-500/30 bg-yellow-500/5",
    low: "border-blue-500/30 bg-blue-500/5",
  };

  return (
    <div
      className={`border rounded-xl p-4 space-y-3 ${
        priorityColors[plan.priority] || priorityColors.medium
      }`}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-sm">{plan.title}</h3>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-500">{plan.estimated_effort}</span>
          <span
            className={`text-xs px-2 py-0.5 rounded font-medium ${
              plan.priority === "critical"
                ? "bg-red-500/20 text-red-400"
                : plan.priority === "high"
                ? "bg-orange-500/20 text-orange-400"
                : "bg-yellow-500/20 text-yellow-400"
            }`}
          >
            {plan.priority.toUpperCase()}
          </span>
        </div>
      </div>

      {plan.steps.length > 0 && (
        <div className="space-y-1">
          <span className="text-xs text-gray-500 font-medium">Steps:</span>
          <ol className="list-decimal list-inside space-y-0.5">
            {plan.steps.map((step, i) => (
              <li key={i} className="text-xs text-gray-400">
                {step}
              </li>
            ))}
          </ol>
        </div>
      )}

      {plan.commands.length > 0 && (
        <div className="space-y-1.5">
          <div className="flex items-center gap-1.5">
            <Terminal className="w-3 h-3 text-gray-500" />
            <span className="text-xs text-gray-500 font-medium">Commands:</span>
          </div>
          {plan.commands.map((cmd, i) => (
            <div
              key={i}
              className="flex items-center gap-2 bg-[#0a0a0a] rounded-lg px-3 py-2 group"
            >
              <code className="text-xs text-green-400 font-mono flex-1 overflow-x-auto">
                {cmd}
              </code>
              <button
                onClick={() => copyCommand(cmd, i)}
                className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
              >
                {copied === i ? (
                  <Check className="w-3.5 h-3.5 text-green-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5 text-gray-500 hover:text-gray-300" />
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
