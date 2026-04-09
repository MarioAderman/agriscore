"use client";

import { motion } from "framer-motion";
import {
  Sun,
  CheckCircle,
  Droplets,
  TrendingUp,
  TriangleAlert,
} from "lucide-react";
import Card from "@/components/ui/Card";
import TrafficLight from "@/components/ui/TrafficLight";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

interface ConditionCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function ConditionCard({ icon, label, value }: ConditionCardProps) {
  return (
    <Card className="flex flex-col items-center gap-2 py-3">
      <p className="text-[#c4c4c4] text-[11px] font-bold text-center leading-tight">
        {label}
      </p>
      {icon}
      <p className="text-white text-[11px] text-center">{value}</p>
    </Card>
  );
}

export default function DailySummary() {
  return (
    <motion.div initial="hidden" animate="visible" className="mt-4">
      <motion.h2
        variants={fadeUp}
        custom={0}
        className="text-xl font-bold text-white"
      >
        Condiciones actuales
      </motion.h2>

      {/* 2x2 conditions grid */}
      <motion.div
        variants={fadeUp}
        custom={1}
        className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4"
      >
        <ConditionCard
          icon={<Sun size={24} className="text-caution" />}
          label="Clima de hoy"
          value="Soleado"
        />
        <ConditionCard
          icon={<CheckCircle size={24} className="text-accent-ui" />}
          label="Salud del cultivo"
          value="Óptimo"
        />
        <ConditionCard
          icon={<Droplets size={24} className="text-blue-400" />}
          label="Humedad estimada"
          value="75%"
        />
        <Card className="flex flex-col items-center gap-2 py-3">
          <p className="text-[#c4c4c4] text-[11px] font-bold text-center leading-tight">
            Crecimiento semanal
          </p>
          <div className="flex items-center gap-1">
            <TrendingUp size={24} className="text-accent" />
            <span className="text-white text-2xl font-bold">5%</span>
          </div>
        </Card>
      </motion.div>

      {/* Alerts */}
      <motion.div variants={fadeUp} custom={2}>
        <Card className="mt-3 flex flex-col items-center gap-2 py-3">
          <p className="text-[#c4c4c4] text-[11px] font-bold text-center">
            Alertas
          </p>
          <TriangleAlert size={20} className="text-warning" />
          <p className="text-white text-[10px] text-center leading-tight px-4">
            Se pronostican lluvias torrenciales la próxima semana
          </p>
        </Card>
      </motion.div>

      {/* Traffic light */}
      <motion.div variants={fadeUp} custom={3}>
        <Card className="mt-3 flex flex-col items-center gap-3 py-4">
          <p className="text-[#c4c4c4] text-[11px] font-bold text-center">
            Estado general del cultivo
          </p>
          <TrafficLight level={3} />
        </Card>
      </motion.div>
    </motion.div>
  );
}
