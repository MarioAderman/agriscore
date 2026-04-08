"use client";

import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import WhatsAppFAB from "@/components/ui/WhatsAppFAB";
import { useFarmerProfile } from "@/hooks/use-farmer-data";
import { MapPin, Phone, Globe, Calendar } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

const profileFields = [
  {
    icon: Phone,
    label: "Teléfono",
    value: "(+52) 961-123-4567",
  },
  {
    icon: MapPin,
    label: "Localización",
    value: "Sindicatura de Costa Rica, Culiacán, Sinaloa, México",
  },
  {
    icon: Globe,
    label: "Idioma/Lenguaje",
    value: "Español",
  },
  {
    icon: Calendar,
    label: "Miembro desde",
    value: "Mayo 2024",
  },
];

export default function PerfilPage() {
  const { data: farmer } = useFarmerProfile();

  return (
    <AppShell>
      <div className="pt-6 md:pt-10">
        <p className="text-xs text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-2xl font-bold text-white mt-6">Mi perfil</h1>

        <motion.div initial="hidden" animate="visible">
          {/* Avatar */}
          <motion.div
            variants={fadeUp}
            custom={0}
            className="mt-6 flex flex-col items-center md:items-start"
          >
            <div className="w-20 h-[75px] rounded-full bg-[#bbf7d0] flex items-center justify-center text-4xl">
              🧑‍🌾
            </div>
            <p className="text-white font-bold text-lg mt-3">{farmer.name}</p>
          </motion.div>

          {/* Data card */}
          <motion.div
            variants={fadeUp}
            custom={1}
            className="mt-6 bg-bg-card rounded-card-lg p-5"
          >
            <h2 className="text-base font-bold text-white mb-4">
              Datos Personales
            </h2>

            <div className="space-y-4">
              {/* Name + CURP */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <p className="text-text-label text-[11px]">Nombre completo</p>
                  <p className="text-white text-sm">{farmer.name}</p>
                </div>
                <div>
                  <p className="text-text-label text-[11px]">CURP</p>
                  <p className="text-white text-sm">JRLP920315HDFLRS09</p>
                </div>
              </div>

              {/* Fields with icons */}
              {profileFields.map((field) => {
                const Icon = field.icon;
                return (
                  <div key={field.label} className="flex items-start gap-3">
                    <Icon
                      size={16}
                      className="text-accent shrink-0 mt-0.5"
                    />
                    <div>
                      <p className="text-text-label text-[11px]">
                        {field.label}
                      </p>
                      <p className="text-white text-sm">{field.value}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      </div>

      <WhatsAppFAB />
    </AppShell>
  );
}
