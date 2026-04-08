"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  MapPin,
  FileBarChart,
  Trophy,
  UserCircle,
  Sprout,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Tab {
  href: string;
  label: string;
  icon: typeof Home;
  hasDot?: boolean;
}

const tabs: Tab[] = [
  { href: "/inicio", label: "Inicio", icon: Home },
  { href: "/cultivo", label: "Mi cultivo", icon: MapPin },
  { href: "/reporte", label: "Reporte", icon: FileBarChart },
  { href: "/retos", label: "Retos", icon: Trophy, hasDot: true },
  { href: "/perfil", label: "Perfil", icon: UserCircle },
];

export default function SideNav() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-[220px] lg:w-[260px] bg-bg-darker min-h-dvh fixed left-0 top-0 bottom-0 z-40">
      {/* Logo */}
      <div className="flex items-center gap-2 px-6 pt-8 pb-6">
        <Sprout size={28} className="text-accent" />
        <span className="text-xl font-bold text-white">AgriScore</span>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 space-y-1">
        {tabs.map((tab) => {
          const isActive =
            pathname === tab.href || pathname === `${tab.href}/`;
          const Icon = tab.icon;

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-card transition-colors duration-200",
                isActive
                  ? "bg-accent/10 text-accent-bright"
                  : "text-text-nav-inactive hover:bg-white/5 hover:text-text-secondary"
              )}
            >
              <div className="relative">
                <Icon size={20} strokeWidth={1.8} />
                {tab.hasDot && (
                  <span className="absolute -top-0.5 -right-0.5 w-[7px] h-[7px] bg-danger rounded-full" />
                )}
              </div>
              <span className="text-sm font-medium">{tab.label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-accent-bright" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-5 border-t border-white/5">
        <p className="text-[10px] text-text-nav-inactive">
          AgriScore v1.0 — Fintegra
        </p>
      </div>
    </aside>
  );
}
