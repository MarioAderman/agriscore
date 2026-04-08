"use client";

import { useEffect, useState } from "react";

interface DataPoint {
  label: string;
  value: number;
}

interface LineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  /** Min/max of Y axis */
  yMin?: number;
  yMax?: number;
  /** Number of horizontal grid lines */
  gridLines?: number;
  /** Highlight the current (last) month label */
  highlightLast?: boolean;
  color?: string;
}

export default function LineChart({
  data,
  width = 320,
  height = 200,
  yMin,
  yMax,
  gridLines = 5,
  highlightLast = true,
  color = "#7be366",
}: LineChartProps) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(t);
  }, []);

  if (data.length === 0) return null;

  const padding = { top: 10, right: 15, bottom: 30, left: 40 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const values = data.map((d) => d.value);
  const minV = yMin ?? Math.min(...values) - 10;
  const maxV = yMax ?? Math.max(...values) + 10;
  const range = maxV - minV || 1;

  const points = data.map((d, i) => ({
    x: padding.left + (i / (data.length - 1)) * chartW,
    y: padding.top + chartH - ((d.value - minV) / range) * chartH,
  }));

  // Build SVG path (smooth quadratic bezier)
  let pathD = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    const prev = points[i - 1];
    const curr = points[i];
    const cpX = (prev.x + curr.x) / 2;
    pathD += ` Q ${cpX} ${prev.y} ${(cpX + curr.x) / 2} ${(prev.y + curr.y) / 2}`;
  }
  // Final segment to last point
  if (points.length > 1) {
    const last = points[points.length - 1];
    pathD += ` T ${last.x} ${last.y}`;
  }

  // Area fill path
  const lastPt = points[points.length - 1];
  const firstPt = points[0];
  const areaD = `${pathD} L ${lastPt.x} ${padding.top + chartH} L ${firstPt.x} ${padding.top + chartH} Z`;

  // Grid lines
  const gridValues = Array.from({ length: gridLines }, (_, i) =>
    Math.round(minV + (i / (gridLines - 1)) * range)
  );

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height}>
      <defs>
        <linearGradient id={`chartGradient-${color}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.3} />
          <stop offset="100%" stopColor={color} stopOpacity={0.02} />
        </linearGradient>
      </defs>

      {/* Grid lines */}
      {gridValues.map((v) => {
        const y = padding.top + chartH - ((v - minV) / range) * chartH;
        return (
          <g key={v}>
            <line
              x1={padding.left}
              y1={y}
              x2={width - padding.right}
              y2={y}
              stroke="rgba(255,255,255,0.06)"
              strokeWidth={1}
            />
            <text
              x={padding.left - 6}
              y={y + 4}
              textAnchor="end"
              fill="#91919f"
              fontSize={12}
              fontWeight={600}
              fontFamily="Noto Sans, sans-serif"
            >
              {v}
            </text>
          </g>
        );
      })}

      {/* Area fill */}
      <path
        d={areaD}
        fill={`url(#chartGradient-${color})`}
        opacity={animated ? 1 : 0}
        style={{ transition: "opacity 0.6s ease" }}
      />

      {/* Line */}
      <path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={animated ? 1 : 0}
        style={{ transition: "opacity 0.4s ease" }}
      />

      {/* Data points */}
      {points.map((p, i) => (
        <circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={3}
          fill={color}
          opacity={animated ? 1 : 0}
          style={{ transition: `opacity 0.4s ease ${i * 0.08}s` }}
        />
      ))}

      {/* X-axis labels */}
      {data.map((d, i) => {
        const isLast = highlightLast && i === data.length - 1;
        return (
          <text
            key={i}
            x={points[i].x}
            y={height - 6}
            textAnchor="middle"
            fill={isLast ? "#91919f" : "#91919f"}
            fontSize={12}
            fontWeight={isLast ? 900 : 600}
            fontFamily="Noto Sans, sans-serif"
            opacity={isLast ? 1 : 0.7}
          >
            {d.label}
          </text>
        );
      })}
    </svg>
  );
}
