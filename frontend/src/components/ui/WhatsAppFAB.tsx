"use client";

import { useState } from "react";
import { MessageCircle } from "lucide-react";

const WHATSAPP_URL = "https://wa.me/5215551234567?text=Hola%2C%20necesito%20ayuda%20con%20mi%20AgriScore";

export default function WhatsAppFAB() {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="fixed bottom-16 md:bottom-8 right-4 md:right-8 z-40" style={{ marginBottom: "env(safe-area-inset-bottom)" }}>
      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute bottom-16 right-0 bg-bg-card-alt rounded-card p-3 shadow-lg w-[220px] text-xs text-white">
          ¿Tienes preguntas? ¡Chatea con nuestro Agente de IA en WhatsApp!
          <div className="absolute bottom-[-6px] right-6 w-3 h-3 bg-bg-card-alt rotate-45" />
        </div>
      )}

      <a
        href={WHATSAPP_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="w-14 h-14 rounded-full bg-[#25D366] flex items-center justify-center shadow-[0_4px_12px_rgba(37,211,102,0.4)] hover:scale-105 transition-transform"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(false)}
      >
        <MessageCircle size={28} className="text-white" fill="white" />
      </a>
    </div>
  );
}
