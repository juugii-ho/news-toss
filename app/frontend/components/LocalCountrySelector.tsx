"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useTransition } from "react";

const options = [
  { code: "KR", label: "🇰🇷 한국" },
  { code: "US", label: "🇺🇸 미국" },
  { code: "JP", label: "🇯🇵 일본" },
  { code: "GB", label: "🇬🇧 영국" }
];

export function LocalCountrySelector() {
  const router = useRouter();
  const params = useSearchParams();
  const current = params.get("country") || "KR";
  const [pending, startTransition] = useTransition();

  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
      <span style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>국가</span>
      <select
        value={current}
        disabled={pending}
        onChange={(e) => {
          const next = e.target.value;
          startTransition(() => {
            router.push(`/local?country=${next}`);
          });
        }}
        style={{
          padding: "8px 10px",
          borderRadius: 10,
          border: "1px solid #e2e8f0",
          fontWeight: 700,
          background: "#fff"
        }}
      >
        {options.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
