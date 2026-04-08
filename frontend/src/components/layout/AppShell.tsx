"use client";

import BottomNav from "./BottomNav";
import SideNav from "./SideNav";

export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-dvh bg-bg-primary">
      {/* Desktop sidebar */}
      <SideNav />

      {/* Main content area — offset on desktop for sidebar */}
      <main
        className="md:ml-[220px] lg:ml-[260px] pb-20 md:pb-8"
        style={{ paddingTop: "env(safe-area-inset-top)" }}
      >
        <div className="w-full px-5 sm:px-8 md:px-10 lg:px-16 xl:px-20">
          {children}
        </div>
      </main>

      {/* Mobile bottom nav */}
      <BottomNav />
    </div>
  );
}
