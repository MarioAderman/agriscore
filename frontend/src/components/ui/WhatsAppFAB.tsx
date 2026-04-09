"use client";

import { useState } from "react";
import { MessageCircle } from "lucide-react";

const WHATSAPP_URL = "https://wa.me/5215551234567?text=Hola%2C%20necesito%20ayuda%20con%20mi%20AgriScore";

interface WhatsAppFABProps {
  showTooltipDefault?: boolean;
}

export default function WhatsAppFAB({ showTooltipDefault = false }: WhatsAppFABProps) {
  const [showTooltip, setShowTooltip] = useState(showTooltipDefault);

  return (
    <div className="fixed bottom-16 md:bottom-6 right-3 md:right-6 z-40" style={{ marginBottom: "env(safe-area-inset-bottom)" }}>
      {/* Tooltip speech bubble */}
      {showTooltip && (
        <div className="absolute bottom-14 right-0 bg-bg-card-alt rounded-card p-2.5 shadow-lg w-[180px] text-[11px] text-white">
          <p className="text-center leading-relaxed">
            ¿Tienes preguntas?<br />
            ¡Chatea con nuestro Agente de IA en WhatsApp!
          </p>
          <div className="absolute bottom-[-6px] right-6 w-3 h-3 bg-bg-card-alt rotate-45" />
        </div>
      )}

      <a
        href={WHATSAPP_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="w-12 h-12 rounded-full bg-[#25D366] flex items-center justify-center shadow-[0_3px_10px_rgba(37,211,102,0.4)] hover:scale-105 transition-transform"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => !showTooltipDefault && setShowTooltip(false)}
        onClick={() => setShowTooltip(false)}
      >
        <MessageCircle size={22} className="text-white" fill="white" />
      </a>
    </div>
  );
}
