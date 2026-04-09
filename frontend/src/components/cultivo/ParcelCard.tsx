import { MapPin, Maximize, Wheat, Droplets } from "lucide-react";
import type { Parcela } from "@/types/farmer";

interface ParcelCardProps {
  parcela: Parcela;
}

export default function ParcelCard({ parcela }: ParcelCardProps) {
  const fields = [
    {
      icon: MapPin,
      label: "Coordenadas GPS:",
      value: `${parcela.latitude.toFixed(4)}\u00B0 N, ${Math.abs(parcela.longitude).toFixed(4)}\u00B0 W`,
      iconColor: "text-danger",
    },
    {
      icon: Maximize,
      label: "Tamaño del terreno:",
      value: `${parcela.area_hectares} Hectáreas`,
      iconColor: "text-accent",
    },
    {
      icon: Wheat,
      label: "Tipo de cultivo:",
      value: "Maíz y cereales / Frijol",
      iconColor: "text-accent",
    },
    {
      icon: Droplets,
      label: "Sistema de riego:",
      value: "Temporal (lluvia)",
      iconColor: "text-accent",
    },
  ];

  return (
    <div className="bg-bg-card-alt rounded-card-lg p-4">
      <h3 className="text-sm font-bold text-white mb-3 text-center italic">
        Ficha técnica
      </h3>
      <div className="space-y-2.5">
        {fields.map((f) => {
          const Icon = f.icon;
          return (
            <div key={f.label} className="flex items-start gap-2.5">
              <Icon size={14} className={`${f.iconColor} mt-0.5 shrink-0`} />
              <div>
                <span className="text-[11px] text-text-secondary font-bold">
                  {f.label}
                </span>{" "}
                <span className="text-[11px] text-white">{f.value}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
