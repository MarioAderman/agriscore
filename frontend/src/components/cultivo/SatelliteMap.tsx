"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

interface SatelliteMapProps {
  imageUrl?: string;
}

const legend = [
  { color: "#8B6914", label: "Suelo desnudo/agua" },
  { color: "#C8B400", label: "Vegetación escasa" },
  { color: "#4CAF50", label: "Cultivos moderados" },
  { color: "#1B5E20", label: "Vegetación densa" },
];

export default function SatelliteMap({ imageUrl }: SatelliteMapProps) {
  return (
    <div className="bg-bg-card-alt rounded-card-lg overflow-hidden">
      {/* Map area */}
      <div className="relative h-[220px] bg-bg-darkest">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Imagen satelital NDVI"
            className="w-full h-full object-cover"
          />
        ) : (
          /* Placeholder pattern */
          <div className="w-full h-full flex items-center justify-center">
            <div
              className="w-full h-full opacity-30"
              style={{
                background: `repeating-linear-gradient(
                  45deg,
                  #2d5a1e 0px, #2d5a1e 10px,
                  #4a7c3f 10px, #4a7c3f 20px,
                  #8fbc45 20px, #8fbc45 30px,
                  #c8b400 30px, #c8b400 40px
                )`,
              }}
            />
            <span className="absolute text-text-muted text-sm">
              Imagen satelital
            </span>
          </div>
        )}

        {/* Navigation arrows */}
        <button className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-black/40 rounded-full flex items-center justify-center">
          <ChevronLeft size={18} className="text-white" />
        </button>
        <button className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-black/40 rounded-full flex items-center justify-center">
          <ChevronRight size={18} className="text-white" />
        </button>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-3 px-3 py-2.5 flex-wrap">
        {legend.map((l) => (
          <div key={l.label} className="flex items-center gap-1">
            <div
              className="w-2.5 h-2.5 rounded-sm"
              style={{ backgroundColor: l.color }}
            />
            <span className="text-[9px] text-text-label">{l.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
