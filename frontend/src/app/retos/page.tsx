"use client";

import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import ChallengeCard from "@/components/retos/ChallengeCard";
import { CHALLENGE_CATEGORIES } from "@/lib/mock-data";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

export default function RetosPage() {
  const available = CHALLENGE_CATEGORIES.filter(
    (c) => c.completed < c.total
  );
  const completed = CHALLENGE_CATEGORIES.filter(
    (c) => c.completed >= c.total
  );

  return (
    <AppShell>
      <div className="pt-6 md:pt-10">
        <p className="text-xs text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-2xl font-bold text-white mt-6">Muro de Retos</h1>
        <p className="text-sm text-text-secondary mt-1">
          Sube tu puntaje de AgriScore y aumenta tus probabilidades de mejorar
          tu crédito
        </p>

        {/* Available challenges */}
        <motion.div initial="hidden" animate="visible" className="mt-5">
          <h2 className="text-base font-bold text-white mb-3">
            Retos disponibles
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {available.map((cat, i) => (
              <motion.div key={cat.tag} variants={fadeUp} custom={i}>
                <ChallengeCard
                  emoji={cat.emoji}
                  tag={cat.tag}
                  total={cat.total}
                  completed={cat.completed}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Completed challenges */}
        {completed.length > 0 && (
          <motion.div
            initial="hidden"
            animate="visible"
            className="mt-6"
          >
            <h2 className="text-base font-bold text-white mb-3">
              Retos completados
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {completed.map((cat, i) => (
                <motion.div
                  key={cat.tag}
                  variants={fadeUp}
                  custom={i + available.length}
                >
                  <ChallengeCard
                    emoji={cat.emoji}
                    tag={cat.tag}
                    total={cat.total}
                    completed={cat.completed}
                  />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
