"use client";

interface RiskItem {
  label: string;
  score: number;
  category: string;
}

interface RiskMatrixProps {
  items: RiskItem[];
}

function getScoreColor(score: number): string {
  if (score >= 90) return "bg-red-500";
  if (score >= 70) return "bg-orange-500";
  if (score >= 40) return "bg-yellow-500";
  return "bg-blue-500";
}

function getScoreLabel(score: number): string {
  if (score >= 90) return "CRITICAL";
  if (score >= 70) return "HIGH";
  if (score >= 40) return "MEDIUM";
  return "LOW";
}

export default function RiskMatrix({ items }: RiskMatrixProps) {
  const sorted = [...items].sort((a, b) => b.score - a.score);

  return (
    <div className="bg-[#141414] border border-[#262626] rounded-xl p-4">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Risk Scores
      </h2>
      {sorted.length === 0 ? (
        <p className="text-sm text-gray-600 text-center py-8">
          No risk scores yet
        </p>
      ) : (
        <div className="space-y-3">
          {sorted.map((item, i) => (
            <div key={i} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300 truncate max-w-[70%]">
                  {item.label}
                </span>
                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded ${
                    item.score >= 90
                      ? "bg-red-500/20 text-red-400"
                      : item.score >= 70
                      ? "bg-orange-500/20 text-orange-400"
                      : item.score >= 40
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {item.score}/100
                </span>
              </div>
              <div className="w-full h-2 bg-[#262626] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ${getScoreColor(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <div className="flex justify-between">
                <span className="text-[10px] text-gray-600">{item.category}</span>
                <span className="text-[10px] text-gray-600">{getScoreLabel(item.score)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
