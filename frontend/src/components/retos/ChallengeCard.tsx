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
    <div className="bg-bg-card-alt rounded-card-lg p-4 flex items-center gap-3">
      <span className="text-2xl shrink-0">{emoji}</span>
      <div className="flex-1 min-w-0">
        <p className="text-white text-sm font-semibold truncate">{tag}</p>
        <div className="flex items-center gap-2 mt-1.5">
          <ProgressBar progress={pct} color={getProgressColor(pct)} className="flex-1" />
          <span className="text-text-label text-xs font-medium shrink-0">
            {pct}%
          </span>
        </div>
        <p className="text-text-label text-[10px] mt-1">
          {total} retos · {completed} completados
        </p>
      </div>
    </div>
  );
}
