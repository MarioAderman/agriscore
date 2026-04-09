"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, MapPin, Trophy, UserCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Tab {
  href: string;
  label: string;
  icon: typeof Home;
  isCenter?: boolean;
}

const tabs: Tab[] = [
  { href: "/cultivo", label: "Mi cultivo", icon: MapPin },
  { href: "/inicio", label: "Inicio", icon: Home, isCenter: true },
  { href: "/retos", label: "Retos", icon: Trophy },
  { href: "/perfil", label: "Perfil", icon: UserCircle },
];

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
      <div
        className="flex items-end justify-around px-1 pt-1.5 bg-bg-nav/95 backdrop-blur-[10px]"
        style={{ paddingBottom: "max(0.35rem, env(safe-area-inset-bottom))" }}
      >
        {tabs.map((tab) => {
          const isActive =
            pathname === tab.href || pathname === `${tab.href}/`;
          const Icon = tab.icon;

          if (tab.isCenter) {
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className="flex flex-col items-center gap-0.5 -mt-3 relative"
              >
                <div
                  className={cn(
                    "w-11 h-11 rounded-full flex items-center justify-center shadow-[0_3px_10px_rgba(74,222,128,0.3)]",
                    isActive ? "bg-accent" : "bg-accent/70"
                  )}
                >
                  <Icon
                    size={20}
                    strokeWidth={2}
                    className="text-bg-darkest"
                  />
                </div>
                <span
                  className={cn(
                    "text-[8px] font-medium leading-none",
                    isActive ? "text-accent-bright" : "text-text-nav-inactive"
                  )}
                >
                  {tab.label}
                </span>
              </Link>
            );
          }

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex flex-col items-center gap-0.5 py-1 px-2.5 relative",
                "transition-colors duration-200"
              )}
            >
              <Icon
                size={18}
                strokeWidth={1.8}
                className={cn(
                  isActive ? "text-accent-bright" : "text-text-nav-inactive"
                )}
              />
              <span
                className={cn(
                  "text-[8px] font-medium leading-none",
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
