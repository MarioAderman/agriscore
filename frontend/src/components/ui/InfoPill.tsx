import { cn } from "@/lib/utils";

interface InfoPillProps {
  label: string;
  value: string;
  className?: string;
}

export default function InfoPill({ label, value, className }: InfoPillProps) {
  return (
    <div
      className={cn(
        "bg-[#547ba4]/20 rounded-[10px] px-4 py-2 text-center",
        className
      )}
    >
      <span className="text-[#c4c4c4] text-xs font-bold">{label}</span>{" "}
      <span className="text-white text-xs">{value}</span>
    </div>
  );
}
