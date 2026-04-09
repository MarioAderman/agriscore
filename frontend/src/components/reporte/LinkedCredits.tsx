"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, ChevronDown, Eye, Phone } from "lucide-react";

interface Credit {
  id: string;
  name: string;
  customer: string;
  amount: string;
  nextPayment: string;
  nextPaymentDate: string;
  icon: string;
  iconBg: string;
}

const credits: Credit[] = [
  {
    id: "1",
    name: "Crédito Agrícola 1",
    customer: "Nombre del Banco 1",
    amount: "$1,000,000",
    nextPayment: "$15,000",
    nextPaymentDate: "01 de Abril 2026",
    icon: "🏦",
    iconBg: "bg-blue-600",
  },
  {
    id: "2",
    name: "Crédito Agrícola 2",
    customer: "Nombre del Banco 2",
    amount: "$500,000",
    nextPayment: "$8,000",
    nextPaymentDate: "15 de Abril 2026",
    icon: "🏦",
    iconBg: "bg-emerald-600",
  },
];

export default function LinkedCredits() {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-3">
      <h2 className="text-xl font-bold text-white">Créditos vinculados</h2>

      {credits.map((credit) => {
        const isOpen = expanded === credit.id;
        return (
          <div
            key={credit.id}
            className="bg-bg-card-alt rounded-card-lg overflow-hidden shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)]"
          >
            {/* Header */}
            <button
              onClick={() => setExpanded(isOpen ? null : credit.id)}
              className="w-full flex items-center gap-3 p-4"
            >
              <div
                className={`w-8 h-8 rounded-lg ${credit.iconBg} flex items-center justify-center text-sm`}
              >
                {credit.icon}
              </div>
              <div className="flex-1 text-left">
                <p className="text-white text-sm font-semibold">
                  {credit.name}
                </p>
                <p className="text-text-label text-xs">{credit.customer}</p>
              </div>
              {isOpen ? (
                <ChevronDown size={18} className="text-text-muted" />
              ) : (
                <ChevronRight size={18} className="text-text-muted" />
              )}
            </button>

            {/* Expanded details */}
            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 space-y-3">
                    <div className="flex items-baseline gap-2">
                      <span className="text-accent-vivid text-lg font-bold">
                        Monto total
                      </span>
                      <span className="text-white text-lg">=</span>
                      <span className="text-white text-xl font-bold">
                        {credit.amount}
                      </span>
                    </div>
                    <div>
                      <p className="text-white text-sm font-bold">
                        Próximo pago{" "}
                        <span className="font-normal">=</span>{" "}
                        <span className="text-white">{credit.nextPayment}</span>
                      </p>
                      <p className="text-text-label text-xs mt-0.5">
                        Fecha de pago: {credit.nextPaymentDate}
                      </p>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-3">
                      <button className="flex-1 flex items-center justify-center gap-2 bg-bg-card rounded-card py-2.5 text-white text-xs font-medium">
                        <Eye size={14} />
                        Ver detalles del crédito
                      </button>
                      <button className="flex-1 flex items-center justify-center gap-2 bg-bg-card rounded-card py-2.5 text-white text-xs font-medium">
                        <Phone size={14} />
                        Contactar al banco
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}

      {/* Encouragement text */}
      <p className="text-xs text-center leading-tight mt-3 px-2">
        <span className="text-white">¡Mantén tu </span>
        <span className="text-accent-bright font-bold">AgriScore</span>
        <span className="text-white">
          {" "}alto para que tu banco vea tu buen desempeño en tu próxima
          renovación!
        </span>
      </p>
    </div>
  );
}
