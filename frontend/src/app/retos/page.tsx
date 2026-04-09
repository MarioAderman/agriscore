"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import ChallengeCard from "@/components/retos/ChallengeCard";
import ChallengeList from "@/components/retos/ChallengeList";
import { CHALLENGE_CATEGORIES } from "@/lib/mock-data";
import { ArrowLeft } from "lucide-react";

const DEMO_ITEMS = [
  { label: "Abril - Factura de fertilizante", status: "pending" as const },
  { label: "Abril - Sistema de riego por goteo", status: "pending" as const },
  { label: "Abril - Disposición de desechos", status: "pending" as const },
  { label: "Marzo - Factura de fertilizante", status: "sent" as const },
  { label: "Marzo - Sistema de riego por goteo", status: "pending" as const },
  { label: "Marzo - Disposición de desechos", status: "pending" as const },
  { label: "Febrero - Factura de fertilizante", status: "completed" as const },
  { label: "Febrero - Sistema de riego por goteo", status: "completed" as const },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.4, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

export default function RetosPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const available = CHALLENGE_CATEGORIES.filter(
    (c) => c.completed < c.total
  );
  const completed = CHALLENGE_CATEGORIES.filter(
    (c) => c.completed >= c.total
  );

  const selected = CHALLENGE_CATEGORIES.find((c) => c.tag === selectedCategory);

  return (
    <AppShell>
      <div className="pt-4 md:pt-8">
        <p className="text-[11px] text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-xl font-bold text-white mt-4 text-center md:text-left">
          Muro de Retos
        </h1>
        <p className="text-sm text-text-secondary mt-1 text-center md:text-left italic">
          Sube tu puntaje de AgriScore y aumenta tus probabilidades de mejorar
          tu crédito
        </p>

        <AnimatePresence mode="wait">
          {selectedCategory && selected ? (
            <motion.div
              key="detail"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.25 }}
              className="mt-5"
            >
              <button
                onClick={() => setSelectedCategory(null)}
                className="flex items-center gap-1 text-accent text-sm mb-4"
              >
                <ArrowLeft size={16} /> Volver
              </button>
              <ChallengeList
                title={selected.tag}
                emoji={selected.emoji}
                total={selected.total}
                completed={selected.completed}
                items={DEMO_ITEMS}
              />
            </motion.div>
          ) : (
            <motion.div
              key="categories"
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, x: 20 }}
            >
              {/* Available challenges */}
              <motion.div className="mt-5">
                <h2 className="text-base font-bold text-white mb-3">
                  Retos disponibles
                </h2>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                  {available.map((cat, i) => (
                    <motion.div
                      key={cat.tag}
                      variants={fadeUp}
                      custom={i}
                      onClick={() => setSelectedCategory(cat.tag)}
                      className="cursor-pointer"
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

              {/* Completed challenges */}
              {completed.length > 0 && (
                <motion.div className="mt-6">
                  <h2 className="text-base font-bold text-white mb-3">
                    Retos completados
                  </h2>
                  <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                    {completed.map((cat, i) => (
                      <motion.div
                        key={cat.tag}
                        variants={fadeUp}
                        custom={i + available.length}
                        onClick={() => setSelectedCategory(cat.tag)}
                        className="cursor-pointer"
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
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </AppShell>
  );
}
