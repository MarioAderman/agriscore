import { MapPin } from "lucide-react";
import type { Parcela } from "@/types/farmer";

interface ParcelCardProps {
  parcela: Parcela;
}

export default function ParcelCard({ parcela }: ParcelCardProps) {
  const fields = [
    { label: "Coordenadas GPS", value: `${parcela.latitude}, ${parcela.longitude}` },
    { label: "Hectáreas", value: `${parcela.area_hectares} ha` },
    { label: "Tipo de cultivo", value: parcela.crop_type },
    { label: "Tipo de riego", value: "Riego por goteo" },
  ];

  return (
    <div className="bg-bg-card-alt rounded-card-lg p-4">
      <h3 className="text-sm font-bold text-text-secondary mb-3">
        Ficha técnica
      </h3>
      <div className="space-y-2">
        {fields.map((f) => (
          <div key={f.label} className="flex items-start gap-2">
            <MapPin size={12} className="text-accent mt-0.5 shrink-0" />
            <div>
              <span className="text-[11px] text-text-label">{f.label}:</span>{" "}
              <span className="text-[11px] text-white">{f.value}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
