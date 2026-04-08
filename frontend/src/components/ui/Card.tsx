import { cn } from "@/lib/utils";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        "bg-[#547ba4]/20 rounded-[10px] p-4",
        className
      )}
    >
      {children}
    </div>
  );
}
