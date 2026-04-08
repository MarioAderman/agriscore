"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import TogglePill from "@/components/ui/TogglePill";
import ParcelCard from "@/components/cultivo/ParcelCard";
import SatelliteMap from "@/components/cultivo/SatelliteMap";
import LineChart from "@/components/ui/LineChart";
import { useFarmerProfile } from "@/hooks/use-farmer-data";
import { DEMO_PHONE } from "@/lib/mock-data";
import { satelliteImageUrl } from "@/lib/api";

const growthData = [
  { label: "OCT", value: 12 },
  { label: "NOV", value: 18 },
  { label: "DIC", value: 25 },
  { label: "ENE", value: 40 },
  { label: "FEB", value: 55 },
  { label: "MAR", value: 72 },
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
  const [activeTab, setActiveTab] = useState<0 | 1>(0);
  const { data: profile } = useFarmerProfile();
  const parcela = profile.parcela!;
  const ndviUrl = satelliteImageUrl(DEMO_PHONE, "ndvi");

  return (
    <AppShell>
      <div className="pt-6 md:pt-10">
        <p className="text-xs text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-2xl font-bold text-white mt-6">Mi cultivo</h1>

        <div className="mt-3 max-w-md">
          <TogglePill
            options={["Mi parcela", "Historial"]}
            active={activeTab}
            onChange={setActiveTab}
          />
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 0 ? (
            <motion.div
              key="parcela"
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, x: 20 }}
              className="mt-4 space-y-4"
            >
              <motion.div variants={fadeUp} custom={0}>
                <h2 className="text-base font-bold text-accent-bright mb-3">
                  Parcela 1: &quot;Rancho Nuevo&quot;
                </h2>
              </motion.div>

              {/* Responsive: side-by-side on desktop */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <motion.div variants={fadeUp} custom={1}>
                  <ParcelCard parcela={parcela} />
                </motion.div>
                <motion.div variants={fadeUp} custom={2}>
                  <SatelliteMap imageUrl={ndviUrl} />
                </motion.div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="historial"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
              className="mt-4 space-y-4"
            >
              <h2 className="text-base font-bold text-white">Mi parcela</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <SatelliteMap imageUrl={ndviUrl} />
                <div className="bg-bg-card-alt rounded-card-lg p-4">
                  <h3 className="text-sm font-bold text-text-secondary mb-3">
                    Crecimiento histórico del cultivo
                  </h3>
                  <LineChart
                    data={growthData}
                    yMin={0}
                    yMax={100}
                    gridLines={6}
                    height={180}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </AppShell>
  );
}
