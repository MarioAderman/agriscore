"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface TogglePillProps {
  options: [string, string];
  active: 0 | 1;
  onChange: (index: 0 | 1) => void;
}

export default function TogglePill({
  options,
  active,
  onChange,
}: TogglePillProps) {
  return (
    <div
      className={cn(
        "relative flex items-center h-12 rounded-full px-1.5",
        "bg-bg-card-highlight",
        "shadow-[inset_-1px_1px_2px_0px_rgba(41,55,71,0.2),inset_1px_-1px_2px_0px_rgba(41,55,71,0.2),inset_-1px_-1px_2px_0px_rgba(47,63,80,0.9),inset_1px_1px_3px_0px_rgba(41,55,71,0.9)]"
      )}
    >
      {options.map((label, i) => (
        <button
          key={label}
          onClick={() => onChange(i as 0 | 1)}
          className={cn(
            "relative z-10 flex-1 flex items-center justify-center h-[35px] rounded-full px-4 text-sm font-medium transition-colors duration-300",
            active === i ? "text-white" : "text-text-muted opacity-70"
          )}
        >
          {active === i && (
            <motion.div
              layoutId="toggle-active"
              className={cn(
                "absolute inset-0 rounded-full bg-bg-card-elevated",
                "shadow-[-1px_1px_2px_0px_rgba(35,47,60,0.2),1px_-1px_2px_0px_rgba(35,47,60,0.2),-1px_-1px_2px_0px_rgba(53,71,90,0.9),1px_1px_3px_0px_rgba(35,47,60,0.9)]"
              )}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative z-10">{label}</span>
        </button>
      ))}
    </div>
  );
}
