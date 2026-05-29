"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Shield, Search, AlertTriangle, Server, Globe } from "lucide-react";

export default function Home() {
  const [target, setTarget] = useState("");
  const [domain, setDomain] = useState("");
  const [industry, setIndustry] = useState("technology");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleInvestigate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;
    setLoading(true);
    const params = new URLSearchParams({ target, domain, industry });
    router.push(`/dashboard?${params.toString()}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <Shield className="w-12 h-12 text-blue-500" />
            <h1 className="text-4xl font-bold tracking-tight">SentinelAI</h1>
          </div>
          <p className="text-lg text-gray-400">
            Autonomous Infrastructure Threat Intelligence Agent
          </p>
          <p className="text-sm text-gray-500 max-w-lg mx-auto">
            Enter your organization name. SentinelAI will scan the open web for CVEs,
            credential leaks, vendor risks, and security advisories — then correlate
            findings against your infrastructure.
          </p>
        </div>

        <form onSubmit={handleInvestigate} className="space-y-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="Enter organization name (e.g., Acme Corp)"
              className="w-full pl-12 pr-4 py-4 bg-[#141414] border border-[#262626] rounded-xl text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Domain (optional)</label>
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="acme.com"
                className="w-full px-4 py-2 bg-[#141414] border border-[#262626] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Industry</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-4 py-2 bg-[#141414] border border-[#262626] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="ecommerce">E-Commerce</option>
                <option value="saas">SaaS</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={!target.trim() || loading}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-xl text-lg font-semibold transition-colors"
          >
            {loading ? "Launching Investigation..." : "Investigate Threats"}
          </button>
        </form>

        <div className="grid grid-cols-3 gap-4 pt-4">
          <div className="flex flex-col items-center gap-2 p-4 bg-[#141414] border border-[#262626] rounded-lg">
            <AlertTriangle className="w-6 h-6 text-orange-500" />
            <span className="text-xs text-gray-400 text-center">CVE & Advisory Scanning</span>
          </div>
          <div className="flex flex-col items-center gap-2 p-4 bg-[#141414] border border-[#262626] rounded-lg">
            <Server className="w-6 h-6 text-green-500" />
            <span className="text-xs text-gray-400 text-center">Environment Correlation</span>
          </div>
          <div className="flex flex-col items-center gap-2 p-4 bg-[#141414] border border-[#262626] rounded-lg">
            <Globe className="w-6 h-6 text-purple-500" />
            <span className="text-xs text-gray-400 text-center">Vendor Risk Assessment</span>
          </div>
        </div>

        <p className="text-center text-xs text-gray-600">
          Powered by Bright Data &bull; LangGraph &bull; Claude Opus 4.6
        </p>
      </div>
    </div>
  );
}
