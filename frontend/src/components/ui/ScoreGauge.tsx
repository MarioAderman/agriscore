"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface ScoreGaugeProps {
  score: number; // 300-850 display scale
  delta?: number; // e.g. +10
  size?: number;
}

export default function ScoreGauge({
  score,
  delta = 10,
  size = 260,
}: ScoreGaugeProps) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 200);
    return () => clearTimeout(t);
  }, []);

  // Gauge arc math
  const strokeWidth = 18;
  const radius = (size - strokeWidth) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = 2 * Math.PI * radius;

  // Arc spans 270 degrees (from 135° to 405°)
  const arcLength = (270 / 360) * circumference;
  const startAngle = 135;

  // Score progress (300-850 range)
  const progress = Math.min(Math.max((score - 300) / 550, 0), 1);
  const dashOffset = arcLength * (1 - (animated ? progress : 0));

  // Tick marks — precompute and round to avoid hydration mismatches
  const totalTicks = 40;
  const tickRadius = radius + 4;
  const ticks = Array.from({ length: totalTicks }, (_, i) => {
    const angle = startAngle + (i / (totalTicks - 1)) * 270;
    const rad = (angle * Math.PI) / 180;
    const innerR = tickRadius - 8;
    const outerR = tickRadius;
    return {
      x1: +(cx + innerR * Math.cos(rad)).toFixed(2),
      y1: +(cy + innerR * Math.sin(rad)).toFixed(2),
      x2: +(cx + outerR * Math.cos(rad)).toFixed(2),
      y2: +(cy + outerR * Math.sin(rad)).toFixed(2),
      filled: i / (totalTicks - 1) <= progress,
    };
  });

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#e9c64a" />
            <stop offset="30%" stopColor="#b5e833" />
            <stop offset="60%" stopColor="#52eb33" />
            <stop offset="100%" stopColor="#14532d" />
          </linearGradient>
          <filter id="gaugeShadow">
            <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#4ade80" floodOpacity="0.3" />
          </filter>
        </defs>

        {/* Tick marks */}
        {ticks.map((t, i) => (
          <line
            key={i}
            x1={t.x1}
            y1={t.y1}
            x2={t.x2}
            y2={t.y2}
            stroke={t.filled ? "#7be366" : "#364556"}
            strokeWidth={2}
            strokeLinecap="round"
            opacity={t.filled ? 1 : 0.5}
          />
        ))}

        {/* Background track */}
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke="#1b2631"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform={`rotate(${startAngle} ${cx} ${cy})`}
        />

        {/* Inner shadow ring */}
        <circle
          cx={cx}
          cy={cy}
          r={radius - strokeWidth / 2 - 8}
          fill="none"
          stroke="#1b2631"
          strokeWidth={4}
          opacity={0.6}
        />

        {/* Score arc */}
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          transform={`rotate(${startAngle} ${cx} ${cy})`}
          filter="url(#gaugeShadow)"
          style={{
            transition: animated ? "stroke-dashoffset 1.2s ease-out" : "none",
          }}
        />

        {/* Outer decorative ring */}
        <circle
          cx={cx}
          cy={cy}
          r={radius + strokeWidth / 2 + 6}
          fill="none"
          stroke="#273746"
          strokeWidth={1}
          opacity={0.4}
        />

        {/* Inner decorative ring */}
        <circle
          cx={cx}
          cy={cy}
          r={radius - strokeWidth / 2 - 16}
          fill="none"
          stroke="#273746"
          strokeWidth={1}
          opacity={0.3}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <div className="flex items-center gap-1">
          <motion.span
            className="text-[40px] font-bold text-white leading-none"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {score}
          </motion.span>
          {delta > 0 && (
            <motion.div
              className="flex flex-col items-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.4 }}
            >
              <svg width="14" height="10" viewBox="0 0 14 10" fill="none">
                <path d="M7 0L13 10H1L7 0Z" fill="#4ade80" />
              </svg>
              <span className="text-white text-sm font-medium">{delta}</span>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
