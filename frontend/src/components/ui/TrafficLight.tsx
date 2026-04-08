interface TrafficLightProps {
  /** 1=red, 2=yellow, 3=green (active level) */
  level: 1 | 2 | 3;
}

const colors = [
  { bg: "bg-danger", glow: "shadow-[0_0_8px_rgba(239,68,68,0.5)]" },
  { bg: "bg-caution", glow: "shadow-[0_0_8px_rgba(234,179,8,0.5)]" },
  { bg: "bg-accent-ui", glow: "shadow-[0_0_8px_rgba(34,197,94,0.5)]" },
];

export default function TrafficLight({ level }: TrafficLightProps) {
  return (
    <div className="flex items-center gap-1.5">
      {colors.map((c, i) => {
        const isActive = i < level;
        return (
          <div
            key={i}
            className={`w-[34px] h-[34px] rounded-full ${
              isActive ? `${c.bg} ${c.glow}` : "bg-bg-card-highlight opacity-40"
            } transition-all duration-500`}
          />
        );
      })}
    </div>
  );
}
