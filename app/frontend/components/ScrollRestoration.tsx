"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";

export function ScrollRestoration() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const key = `${pathname}?${searchParams?.toString() ?? ""}`;

  useEffect(() => {
    const save = () => {
      try {
        sessionStorage.setItem(`scroll:${key}`, String(window.scrollY));
      } catch {
        // ignore storage errors in private mode
      }
    };

    const restore = () => {
      try {
        const stored = sessionStorage.getItem(`scroll:${key}`);
        if (stored) {
          const y = parseInt(stored, 10);
          if (!Number.isNaN(y)) {
            requestAnimationFrame(() => window.scrollTo(0, y));
          }
        }
      } catch {
        // ignore storage errors
      }
    };

    restore();
    window.addEventListener("beforeunload", save);
    window.addEventListener("pagehide", save);

    return () => {
      save();
      window.removeEventListener("beforeunload", save);
      window.removeEventListener("pagehide", save);
    };
  }, [key]);

  return null;
}
