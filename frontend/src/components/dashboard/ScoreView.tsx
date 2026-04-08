"use client";

import { motion } from "framer-motion";
import ScoreGauge from "@/components/ui/ScoreGauge";
import InfoPill from "@/components/ui/InfoPill";
import { TriangleAlert } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

interface ScoreViewProps {
  score: number;
  delta: number;
  riskCategory: string;
}

export default function ScoreView({ score, delta, riskCategory }: ScoreViewProps) {
  const confianza = riskCategory === "bajo" ? "Alto" : riskCategory === "moderado" ? "Medio" : "Bajo";

  return (
    <motion.div
      initial="hidden"
      animate="visible"
    >
      {/* Desktop: gauge left, details right. Mobile: stacked centered */}
      <div className="flex flex-col items-center md:flex-row md:items-start md:gap-10 mt-4">
        {/* Gauge — larger on desktop */}
        <motion.div variants={fadeUp} custom={0} className="shrink-0 hidden md:block">
          <ScoreGauge score={score} delta={delta} size={300} />
        </motion.div>
        <motion.div variants={fadeUp} custom={0} className="shrink-0 md:hidden">
          <ScoreGauge score={score} delta={delta} size={240} />
        </motion.div>

        {/* Details column */}
        <div className="flex flex-col items-center md:items-start md:pt-6 w-full md:flex-1">
          {/* Label */}
          <motion.p
            variants={fadeUp}
            custom={1}
            className="text-text-secondary text-xs text-center md:text-left mt-2 md:mt-0"
          >
            Basado en tu actividad agrícola
          </motion.p>

          {/* Info pills */}
          <motion.div
            variants={fadeUp}
            custom={2}
            className="flex gap-3 w-full mt-5"
          >
            <InfoPill label="Tasa Actual:" value="12%" className="flex-1" />
            <InfoPill label="Nivel de Confianza:" value={confianza} className="flex-1" />
          </motion.div>

          {/* Next objective */}
          <motion.div
            variants={fadeUp}
            custom={3}
            className="bg-[#547ba4]/20 rounded-[10px] w-full px-4 py-2.5 mt-3 flex items-center gap-2"
          >
            <TriangleAlert size={15} className="text-accent-dark shrink-0" />
            <p className="text-xs leading-snug">
              <span className="text-accent-dark font-bold">Próximo objetivo:</span>{" "}
              <span className="text-white">Completa 2 retos más para subir</span>
            </p>
          </motion.div>

          {/* Disclaimer */}
          <motion.p
            variants={fadeUp}
            custom={4}
            className="text-text-secondary text-[11px] italic text-center md:text-left mt-4 leading-tight"
          >
            Una puntuación alta en el AgriScore aumenta tus probabilidades de
            mejores condiciones crediticias con los bancos asociados
          </motion.p>
        </div>
      </div>
    </motion.div>
  );
}
