import { Clock, Camera, CheckCircle } from "lucide-react";
import ProgressBar from "@/components/ui/ProgressBar";

interface ChallengeItem {
  label: string;
  status: "pending" | "sent" | "completed";
}

interface ChallengeListProps {
  title: string;
  emoji: string;
  total: number;
  completed: number;
  items: ChallengeItem[];
}

const statusIcon = {
  pending: <Clock size={18} className="text-text-muted" />,
  sent: <Camera size={18} className="text-caution" />,
  completed: <CheckCircle size={18} className="text-accent-ui" />,
};

export default function ChallengeList({
  title,
  emoji,
  total,
  completed,
  items,
}: ChallengeListProps) {
  const pct = Math.round((completed / total) * 100);

  return (
    <div>
      {/* Header */}
      <h2 className="text-lg font-bold text-white">{title}</h2>
      <div className="flex items-center gap-3 mt-2">
        <span className="text-2xl">{emoji}</span>
        <ProgressBar progress={pct} color="bg-accent" className="flex-1" />
        <span className="text-sm font-bold text-white">{pct}%</span>
      </div>
      <p className="text-text-label text-xs mt-1">
        {total} Retos - {completed} completados
      </p>

      {/* Items */}
      <div className="mt-4 space-y-2">
        {items.map((item, i) => (
          <div
            key={i}
            className="flex items-center justify-between bg-bg-card-alt rounded-card px-4 py-3"
          >
            <span className="text-sm text-white">{item.label}</span>
            {statusIcon[item.status]}
          </div>
        ))}
      </div>
    </div>
  );
}
