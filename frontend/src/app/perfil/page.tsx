"use client";

import { motion } from "framer-motion";
import AppShell from "@/components/layout/AppShell";
import WhatsAppFAB from "@/components/ui/WhatsAppFAB";
import { useFarmerProfile } from "@/hooks/use-farmer-data";
import { MapPin, Phone, Globe, Calendar, User, FileText } from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] as const },
  }),
};

export default function PerfilPage() {
  const { data: farmer } = useFarmerProfile();

  const profileFields = [
    {
      icon: User,
      label: "Nombre:",
      value: farmer.name,
      iconColor: "text-danger",
    },
    {
      icon: FileText,
      label: "CURP:",
      value: "EUBJ850315HCSSCN05",
      iconColor: "text-danger",
    },
    {
      icon: Phone,
      label: "Teléfono:",
      value: "(+52) 968-100-4567",
      iconColor: "text-danger",
    },
    {
      icon: MapPin,
      label: "Localidad:",
      value: "Ocozocoautla de Espinosa, Chiapas, México",
      iconColor: "text-danger",
    },
    {
      icon: Globe,
      label: "Idioma/Dialecto:",
      value: "Español",
      iconColor: "text-danger",
    },
    {
      icon: Calendar,
      label: "Antigüedad en la Plataforma:",
      value: "Miembro desde: Enero 2019",
      iconColor: "text-danger",
    },
  ];

  return (
    <AppShell>
      <div className="pt-4 md:pt-8">
        <p className="text-[11px] text-text-label text-center md:text-left font-display">
          26 de Marzo del 2026
        </p>

        <h1 className="text-xl font-bold text-white mt-4 text-center md:text-left">
          Mi perfil
        </h1>

        <motion.div initial="hidden" animate="visible">
          {/* Avatar */}
          <motion.div
            variants={fadeUp}
            custom={0}
            className="mt-6 flex flex-col items-center md:items-start"
          >
            <div className="w-16 h-16 rounded-full bg-[#bbf7d0] flex items-center justify-center text-3xl">
              🧑‍🌾
            </div>
          </motion.div>

          {/* Data card */}
          <motion.div
            variants={fadeUp}
            custom={1}
            className="mt-6 bg-bg-card rounded-card-lg p-5"
          >
            <h2 className="text-base font-bold text-white mb-4 text-center md:text-left">
              Datos Personales
            </h2>

            <div className="space-y-4 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-4 md:space-y-0">
              {profileFields.map((field) => {
                const Icon = field.icon;
                return (
                  <div key={field.label} className="flex items-start gap-3">
                    <Icon
                      size={16}
                      className={`${field.iconColor} shrink-0 mt-0.5`}
                    />
                    <div>
                      <span className="text-text-secondary text-[12px] font-bold">
                        {field.label}
                      </span>{" "}
                      <span className="text-white text-sm">{field.value}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      </div>

      <WhatsAppFAB showTooltipDefault />
    </AppShell>
  );
}
