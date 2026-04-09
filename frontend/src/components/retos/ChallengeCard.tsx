import { ChevronRight } from "lucide-react";
import ProgressBar from "@/components/ui/ProgressBar";

interface ChallengeCardProps {
  emoji: string;
  tag: string;
  total: number;
  completed: number;
}

function getProgressColor(pct: number): string {
  if (pct >= 100) return "bg-accent-ui";
  if (pct >= 60) return "bg-accent";
  if (pct >= 30) return "bg-caution";
  return "bg-warning";
}

export default function ChallengeCard({
  emoji,
  tag,
  total,
  completed,
}: ChallengeCardProps) {
  const pct = Math.round((completed / total) * 100);

  return (
    <div className="bg-white/95 rounded-card-lg p-4 flex flex-col gap-2">
      {/* Header row */}
      <div className="flex items-start justify-between">
        <h3 className="text-sm font-bold text-bg-darkest leading-tight flex-1 pr-2">
          {tag}
        </h3>
        <ChevronRight size={16} className="text-bg-card shrink-0 mt-0.5" />
      </div>

      {/* Retos count badge */}
      <div className="flex items-center gap-1">
        <span className="text-[10px] text-bg-card-alt bg-gray-100 rounded px-1.5 py-0.5 font-medium">
          {total} Retos
        </span>
      </div>

      {/* Emoji + progress */}
      <div className="flex items-center gap-3 mt-1">
        <span className="text-2xl">{emoji}</span>
        <div className="flex-1">
          <ProgressBar progress={pct} color={getProgressColor(pct)} />
        </div>
        <span className="text-xs font-bold text-bg-darkest shrink-0">
          {pct}%
        </span>
      </div>
    </div>
  );
}
