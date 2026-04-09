"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import TogglePill from "@/components/ui/TogglePill";
import ScoreOverview from "@/components/reporte/ScoreOverview";
import LinkedCredits from "@/components/reporte/LinkedCredits";
import { useFarmerAgriScore, useFarmerProfile } from "@/hooks/use-farmer-data";
import { FileDown, ChevronRight } from "lucide-react";

export default function ReportePage() {
  const [activeTab, setActiveTab] = useState<0 | 1>(0);
  const { data: profile } = useFarmerProfile();
  const { data: agriscore } = useFarmerAgriScore();

  const score = agriscore.current?.total ?? 0;
  const history = agriscore.history ?? [];
  const firstName = profile.name.split(" ")[0];

  return (
    <AppShell>
      <div className="pt-4 md:pt-8">
        {/* Date */}
        <p className="text-[11px] text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-[26px] font-bold leading-[32px] text-text-secondary mt-3">
          Reporte de crédito
        </h1>

        {/* Greeting */}
        <div className="mt-3">
          <p className="text-accent-vivid text-xl font-bold">Don {firstName},</p>
          <p className="text-white text-base">
            ¡Tu AgriScore está en buena forma!
          </p>
        </div>

        {/* Toggle */}
        <div className="mt-4 max-w-md">
          <TogglePill
            options={["Puntaje", "Créditos"]}
            active={activeTab}
            onChange={setActiveTab}
          />
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 0 ? (
            <motion.div
              key="overview"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.25 }}
              className="mt-5"
            >
              <ScoreOverview score={score} history={history} />
            </motion.div>
          ) : (
            <motion.div
              key="credits"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
              className="mt-5"
            >
              <LinkedCredits />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Monthly report card */}
        <div className="mt-5 bg-bg-card-alt rounded-card p-4 flex items-center gap-4 shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
            <FileDown size={16} className="text-white" />
          </div>
          <div className="flex-1">
            <p className="text-white text-sm font-semibold">
              Reporte mensual de AgriScore
            </p>
            <p className="text-text-label text-xs">Revisa tu historial</p>
          </div>
          <ChevronRight size={18} className="text-text-muted shrink-0" />
        </div>
      </div>
    </AppShell>
  );
}
