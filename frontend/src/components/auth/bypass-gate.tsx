"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ensureBypassSession } from "@/lib/auth";

export function BypassGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [showChildren, setShowChildren] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const redirectIfBypassed = async () => {
      const bypassed = await ensureBypassSession();
      if (cancelled) {
        return;
      }
      if (bypassed) {
        router.replace("/dashboard");
        return;
      }
      setShowChildren(true);
    };

    void redirectIfBypassed();
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!showChildren) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white text-gray-500">
        Loading...
      </div>
    );
  }

  return <>{children}</>;
}
