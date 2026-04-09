"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import TogglePill from "@/components/ui/TogglePill";
import ScoreView from "@/components/dashboard/ScoreView";
import DailySummary from "@/components/dashboard/DailySummary";
import { useFarmerAgriScore, useFarmerProfile } from "@/hooks/use-farmer-data";

export default function InicioPage() {
  const [activeTab, setActiveTab] = useState<0 | 1>(0);
  const { data: profile } = useFarmerProfile();
  const { data: agriscore } = useFarmerAgriScore();

  const score = agriscore.current?.total ?? 0;
  const riskCategory = agriscore.current?.risk_category ?? "alto";
  const firstName = profile.name.split(" ")[0];

  return (
    <AppShell>
      <div className="pt-6 md:pt-10">
        {/* Date */}
        <p className="text-xs text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        {/* Greeting + avatar */}
        <div className="mt-4 flex items-start justify-between">
          <div>
            <h1 className="text-[32px] font-bold leading-[39px] text-text-secondary">
              ¡Buen día,
            </h1>
            <h1 className="text-[32px] font-bold leading-[39px] text-accent-vivid">
              Don {firstName}!
            </h1>
            <p className="text-lg text-white mt-1">Su tierra está sana</p>
          </div>
          <div className="w-[58px] h-[57px] rounded-full bg-accent/20 flex items-center justify-center text-3xl mt-1 shrink-0">
            🧑‍🌾
          </div>
        </div>

        {/* Toggle */}
        <div className="mt-4 max-w-md">
          <TogglePill
            options={["Puntuación actual", "Resumen diario"]}
            active={activeTab}
            onChange={setActiveTab}
          />
        </div>

        {/* Tab content */}
        <AnimatePresence mode="wait">
          {activeTab === 0 ? (
            <motion.div
              key="score"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.25 }}
            >
              <ScoreView
                score={score}
                delta={10}
                riskCategory={riskCategory}
              />
            </motion.div>
          ) : (
            <motion.div
              key="daily"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
            >
              <DailySummary />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </AppShell>
  );
}
