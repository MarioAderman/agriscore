"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";

export default function VerificarPage() {
  const [code, setCode] = useState("");
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push("/inicio/");
  }

  return (
    <div className="min-h-dvh bg-bg-primary flex flex-col items-center px-5 sm:px-8">
      {/* Skip link */}
      <div className="w-full max-w-xs sm:max-w-sm flex justify-end mt-3">
        <Link
          href="/inicio/"
          className="text-[11px] text-text-muted hover:text-accent transition-colors"
        >
          Saltar &rarr;
        </Link>
      </div>

      {/* Date */}
      <p className="text-[11px] text-text-label text-center font-display mt-4 md:mt-6">
        26 de Marzo del 2026
      </p>

      {/* Title */}
      <motion.h1
        className="text-[32px] sm:text-[36px] font-bold text-accent mt-8 sm:mt-10 tracking-tight"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        AgriScore
      </motion.h1>

      {/* Logo */}
      <motion.div
        className="mt-5 sm:mt-6 w-[90px] h-[90px] sm:w-[100px] sm:h-[100px] rounded-full bg-[#d4f5d4]/20 flex items-center justify-center overflow-hidden"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.4 }}
      >
        <img
          src="/logo.png"
          alt="AgriScore"
          className="w-[70px] h-[70px] sm:w-[80px] sm:h-[80px] object-contain"
        />
      </motion.div>

      {/* Form */}
      <motion.form
        onSubmit={handleSubmit}
        className="mt-8 sm:mt-10 w-full max-w-xs sm:max-w-sm"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      >
        <label className="text-white text-sm sm:text-base block mb-2">
          Código:
        </label>
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="000000"
          maxLength={6}
          className="w-full h-11 sm:h-12 rounded-pill bg-bg-card-highlight text-white px-5 text-sm text-center tracking-[0.5em] outline-none focus:ring-2 focus:ring-accent/40 placeholder:text-text-muted placeholder:tracking-[0.5em]"
        />

        <div className="flex flex-col items-center mt-6 gap-2.5">
          <button
            type="submit"
            className="h-10 sm:h-11 px-8 rounded-pill bg-accent/80 text-bg-darkest font-bold text-sm hover:bg-accent transition-colors"
          >
            Validar
          </button>
          <button
            type="button"
            onClick={() => {}}
            className="h-10 sm:h-11 px-8 rounded-pill bg-bg-card-highlight text-white font-medium text-sm hover:bg-bg-card-elevated transition-colors"
          >
            Reenviar código
          </button>
        </div>
      </motion.form>
    </div>
  );
}
