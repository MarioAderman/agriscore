"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  MapPin,
  FileBarChart,
  Trophy,
  UserCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Tab {
  href: string;
  label: string;
  icon: typeof Home;
  isCenter?: boolean;
  hasDot?: boolean;
}

const tabs: Tab[] = [
  { href: "/reporte", label: "Reporte", icon: FileBarChart },
  { href: "/cultivo", label: "Mi cultivo", icon: MapPin },
  { href: "/inicio", label: "Inicio", icon: Home, isCenter: true },
  { href: "/retos", label: "Retos", icon: Trophy, hasDot: true },
  { href: "/perfil", label: "Perfil", icon: UserCircle },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div
        className="flex items-center justify-around px-2 pt-2 bg-bg-nav/95 backdrop-blur-[10px]"
        style={{ paddingBottom: "max(0.5rem, env(safe-area-inset-bottom))" }}
      >
        {tabs.map((tab) => {
          const isActive =
            pathname === tab.href || pathname === `${tab.href}/`;
          const Icon = tab.icon;

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex flex-col items-center gap-0.5 py-1.5 px-3 relative",
                "transition-colors duration-200"
              )}
            >
              <div className="relative">
                <Icon
                  size={20}
                  strokeWidth={1.8}
                  className={cn(
                    isActive ? "text-accent-bright" : "text-text-nav-inactive"
                  )}
                />
                {tab.hasDot && (
                  <span className="absolute -top-0.5 -right-0.5 w-[6px] h-[6px] bg-danger rounded-full" />
                )}
              </div>
              <span
                className={cn(
                  "text-[9px] font-medium leading-none",
                  isActive ? "text-accent-bright" : "text-text-nav-inactive"
                )}
              >
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
