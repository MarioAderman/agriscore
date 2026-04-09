"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface SatelliteImage {
  src: string;
  label: string;
}

interface SatelliteMapProps {
  images?: SatelliteImage[];
  title?: string;
}

const DEFAULT_IMAGES: SatelliteImage[] = [
  { src: "/ndvi-abr-2025.png", label: "Abr 2025" },
  { src: "/ndvi-sep-2025.png", label: "Sep 2025" },
  { src: "/ndvi-ene-2026.png", label: "Ene 2026" },
  { src: "/ndvi-mar-2026.png", label: "Mar 2026" },
];

const legend = [
  { color: "#8B6914", label: "Bare/water" },
  { color: "#C8B400", label: "Sparse veg." },
  { color: "#4CAF50", label: "Moderate (Crops)" },
  { color: "#1B5E20", label: "Dense vegetation" },
];

export default function SatelliteMap({ images = DEFAULT_IMAGES, title = "Mi parcela" }: SatelliteMapProps) {
  const [idx, setIdx] = useState(images.length - 1);
  const current = images[idx];

  function prev() {
    setIdx((i) => (i === 0 ? images.length - 1 : i - 1));
  }
  function next() {
    setIdx((i) => (i === images.length - 1 ? 0 : i + 1));
  }

  return (
    <div className="bg-bg-card-alt rounded-card-lg overflow-hidden">
      {/* Title */}
      <h3 className="text-sm font-bold text-white text-center italic py-3 px-4">
        {title}
      </h3>

      {/* Map area */}
      <div className="relative h-[200px] sm:h-[240px] md:h-[280px] bg-bg-darkest mx-3">
        {/* "Land Classification" label */}
        <div className="absolute top-2 left-2 z-10 bg-black/50 px-2 py-1 rounded text-[10px] text-white font-medium">
          Land Classification
        </div>

        {/* Date label */}
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 z-10 bg-black/60 px-3 py-1 rounded-full text-[10px] text-white font-medium">
          {current.label}
        </div>

        <img
          src={current.src}
          alt={`NDVI — ${current.label}`}
          className="w-full h-full object-cover transition-opacity duration-300"
        />

        {/* Legend overlay */}
        <div className="absolute top-10 right-2 z-10 bg-black/60 rounded p-1.5 space-y-1">
          {legend.map((l) => (
            <div key={l.label} className="flex items-center gap-1.5">
              <div
                className="w-3 h-2.5 rounded-sm"
                style={{ backgroundColor: l.color }}
              />
              <span className="text-[8px] text-white leading-none">{l.label}</span>
            </div>
          ))}
        </div>

        {/* Navigation arrows */}
        {images.length > 1 && (
          <>
            <button
              onClick={prev}
              className="absolute left-1 top-1/2 -translate-y-1/2 w-7 h-7 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center transition-colors"
            >
              <ChevronLeft size={16} className="text-white" />
            </button>
            <button
              onClick={next}
              className="absolute right-1 top-1/2 -translate-y-1/2 w-7 h-7 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center transition-colors"
            >
              <ChevronRight size={16} className="text-white" />
            </button>
          </>
        )}

        {/* Dot indicators */}
        {images.length > 1 && (
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 flex gap-1.5">
            {images.map((_, i) => (
              <div
                key={i}
                className={`w-1.5 h-1.5 rounded-full transition-colors ${
                  i === idx ? "bg-white" : "bg-white/40"
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Bottom spacing */}
      <div className="h-3" />
    </div>
  );
}
