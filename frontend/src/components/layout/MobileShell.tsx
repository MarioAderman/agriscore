"use client";

import BottomNav from "./BottomNav";

export default function MobileShell({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative mx-auto w-full max-w-[430px] min-h-dvh bg-bg-primary">
      <main className="pb-28">{children}</main>
      <BottomNav />
    </div>
  );
}
