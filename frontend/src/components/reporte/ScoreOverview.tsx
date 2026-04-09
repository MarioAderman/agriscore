"use client";

import { motion } from "framer-motion";
import LinearGauge from "@/components/ui/LinearGauge";
import LineChart from "@/components/ui/LineChart";
import type { AgriScoreHistory } from "@/types/farmer";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

const MONTH_LABELS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"];

interface ScoreOverviewProps {
  score: number;
  history: AgriScoreHistory[];
}

export default function ScoreOverview({ score, history }: ScoreOverviewProps) {
  const chartData = history.map((h) => {
    const date = new Date(h.scored_at);
    return {
      label: MONTH_LABELS[date.getMonth()],
      value: h.total,
    };
  });

  return (
    <motion.div initial="hidden" animate="visible">
      {/* Desktop: side by side. Mobile: stacked */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Linear gauge */}
        <motion.div variants={fadeUp} custom={0} className="md:pt-2">
          <LinearGauge score={score} />
        </motion.div>

        {/* Chart */}
        <motion.div variants={fadeUp} custom={1}>
          <p className="text-text-label text-xs text-center mb-3">
            Crecimiento de puntaje crediticio AgriScore
          </p>
          <LineChart
            data={chartData}
            yMin={300}
            yMax={850}
            gridLines={6}
            height={220}
          />
        </motion.div>
      </div>
    </motion.div>
  );
}
