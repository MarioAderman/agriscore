interface LinearGaugeProps {
  /** Score on 300-850 scale */
  score: number;
  min?: number;
  max?: number;
}

const segments = [
  { color: "#dc6050", flex: 1 },
  { color: "#e19951", flex: 1 },
  { color: "#e9c64a", flex: 0.8 },
  { color: "#dfe744", flex: 1.2 },
  { color: "#b5e833", flex: 0.8 },
  { color: "#52eb33", flex: 0.5 },
];

export default function LinearGauge({
  score,
  min = 300,
  max = 850,
}: LinearGaugeProps) {
  const progress = Math.min(Math.max((score - min) / (max - min), 0), 1);
  const labels = [min, 560, max];

  return (
    <div className="w-full">
      {/* Score + badge */}
      <div className="flex items-baseline justify-between mb-2">
        <p className="text-sm font-semibold">
          <span className="text-accent-bright">{score}</span>
          <span className="text-text-label"> / {max}</span>
        </p>
        <span className="text-accent-bright text-sm font-semibold">
          EXCELENTE
        </span>
      </div>

      {/* Gauge bar */}
      <div className="relative h-[22px] rounded-full overflow-hidden flex">
        {segments.map((seg, i) => (
          <div
            key={i}
            className="h-full"
            style={{
              flex: seg.flex,
              backgroundColor: seg.color,
              borderRadius:
                i === 0
                  ? "99px 0 0 99px"
                  : i === segments.length - 1
                  ? "0 99px 99px 0"
                  : undefined,
            }}
          />
        ))}
        {/* Indicator marker */}
        <div
          className="absolute top-0 bottom-0 w-[3px] bg-white shadow-[0_0_6px_rgba(255,255,255,0.8)]"
          style={{ left: `${progress * 100}%`, transform: "translateX(-50%)" }}
        />
      </div>

      {/* Scale labels */}
      <div className="flex justify-between mt-1.5">
        {labels.map((v) => (
          <span key={v} className="text-xs text-[#e1e2e5] font-medium">
            {v}
          </span>
        ))}
      </div>
    </div>
  );
}
