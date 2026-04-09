"use client";

import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import ParcelCard from "@/components/cultivo/ParcelCard";
import SatelliteMap from "@/components/cultivo/SatelliteMap";
import LineChart from "@/components/ui/LineChart";
import { useFarmerProfile } from "@/hooks/use-farmer-data";
import { Settings } from "lucide-react";

const growthData = [
  { label: "OCT", value: 800 },
  { label: "NOV", value: 1200 },
  { label: "DIC", value: 1800 },
  { label: "ENE", value: 2200 },
  { label: "FEB", value: 2800 },
  { label: "MAR", value: 3200 },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

export default function CultivoPage() {
  const { data: profile } = useFarmerProfile();
  const parcela = profile.parcela!;

  return (
    <AppShell>
      <div className="pt-4 md:pt-8">
        <p className="text-[11px] text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-xl font-bold text-white mt-4 text-center md:text-left">
          Mi cultivo
        </h1>

        <motion.div initial="hidden" animate="visible" className="mt-4 space-y-4">
          {/* Parcela title with gear */}
          <motion.div variants={fadeUp} custom={0} className="flex items-center justify-between">
            <h2 className="text-base font-bold text-accent-bright">
              Parcela 287: &quot;Ejido El Ocote&quot;
            </h2>
            <Settings size={18} className="text-text-secondary" />
          </motion.div>

          {/* Desktop: ficha + satellite side-by-side. Mobile: stacked */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <motion.div variants={fadeUp} custom={1}>
              <ParcelCard parcela={parcela} />
            </motion.div>
            <motion.div variants={fadeUp} custom={2}>
              <SatelliteMap title="Mi parcela" />
            </motion.div>
          </div>

          {/* Growth chart */}
          <motion.div variants={fadeUp} custom={3} className="bg-bg-card-alt rounded-card-lg p-4">
            <h3 className="text-sm font-bold text-white mb-3 text-center italic">
              Crecimiento histórico del cultivo
            </h3>
            <LineChart
              data={growthData}
              yMin={0}
              yMax={4000}
              gridLines={5}
              height={180}
            />
          </motion.div>
        </motion.div>
      </div>
    </AppShell>
  );
}
