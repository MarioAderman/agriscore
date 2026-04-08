import { cn } from "@/lib/utils";

interface ProgressBarProps {
  /** 0-100 */
  progress: number;
  color?: string;
  className?: string;
}

export default function ProgressBar({
  progress,
  color = "bg-accent",
  className,
}: ProgressBarProps) {
  const clamped = Math.min(Math.max(progress, 0), 100);
  return (
    <div className={cn("w-full h-2 bg-bg-darkest rounded-full overflow-hidden", className)}>
      <div
        className={cn("h-full rounded-full transition-all duration-700 ease-out", color)}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
