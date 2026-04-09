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
        className="md:ml-[200px] lg:ml-[230px] pb-16 md:pb-6"
        style={{ paddingTop: "env(safe-area-inset-top)" }}
      >
        <div className="w-full px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
          {children}
        </div>
      </main>

      {/* Mobile bottom nav */}
      <BottomNav />
    </div>
  );
}
