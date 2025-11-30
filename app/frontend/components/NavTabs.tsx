"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

const tabs = [
  { href: "/global", label: "Global" },
  { href: "/local", label: "Local" }
];

export function NavTabs() {
  const pathname = usePathname();
  const params = useSearchParams();
  const router = useRouter();
  const [showCountryMenu, setShowCountryMenu] = React.useState(false);

  const isGlobal = pathname === "/" || pathname === "/global" || pathname?.startsWith("/global");
  const isLocal = pathname?.startsWith("/local");
  const includeKr = params.get("kr") !== "exclude";
  const country = params.get("country") || "ALL";

  const countryOptions = [
    { code: "ALL", label: "전체 보기" },
    { code: "AU", label: "🇦🇺 호주" },
    { code: "BE", label: "🇧🇪 벨기에" },
    { code: "CA", label: "🇨🇦 캐나다" },
    { code: "CN", label: "🇨🇳 중국" },
    { code: "DE", label: "🇩🇪 독일" },
    { code: "FR", label: "🇫🇷 프랑스" },
    { code: "GB", label: "🇬🇧 영국" },
    { code: "IT", label: "🇮🇹 이탈리아" },
    { code: "JP", label: "🇯🇵 일본" },
    { code: "KR", label: "🇰🇷 대한민국" },
    { code: "NL", label: "🇳🇱 네덜란드" },
    { code: "RU", label: "🇷🇺 러시아" },
    { code: "US", label: "🇺🇸 미국" }
  ].sort((a, b) => {
    if (a.code === "ALL") return -1;
    if (b.code === "ALL") return 1;
    const nameA = a.label.split(" ")[1] || a.label;
    const nameB = b.label.split(" ")[1] || b.label;
    return nameA.localeCompare(nameB, "ko");
  });

  const handleGlobalToggle = () => {
    const q = new URLSearchParams(params.toString());
    if (includeKr) q.set("kr", "exclude");
    else q.delete("kr");
    router.push(`/global?${q.toString()}`);
  };

  const handleCountrySelect = (code: string) => {
    const q = new URLSearchParams(params.toString());
    if (code === "ALL") q.delete("country");
    else q.set("country", code);
    q.delete("chooseCountry");
    setShowCountryMenu(false);
    router.push(`/local?${q.toString()}`);
  };

  const currentCountryLabel = countryOptions.find(c => c.code === country)?.label || country;

  return (
    <nav
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        alignItems: "center",
        gap: "var(--space-2)",
        padding: "var(--space-2) 0 var(--space-3)",
        position: "sticky",
        top: 0,
        background: "#f8fafc", // Solid color
        zIndex: 20,
        borderBottom: "1px solid var(--color-border)"
      }}
    >
      {tabs.map((tab) => {
        const active =
          pathname === tab.href ||
          pathname?.startsWith(`${tab.href}/`) ||
          (tab.href === "/global" && pathname === "/");
        return (
          <Link
            key={tab.href}
            href={tab.href}
            style={{
              textAlign: "center",
              padding: "var(--space-2) var(--space-3)",
              borderRadius: "var(--radius-md)",
              background: active ? "var(--color-primary-600)" : "#fff",
              color: active ? "#fff" : "var(--color-neutral-900)",
              fontWeight: 800,
              fontSize: 16,
              textDecoration: "none",
              border: `1px solid ${active ? "var(--color-primary-600)" : "var(--color-border)"}`,
              transition: "all var(--transition-fast)",
              // Removed shadow as requested
            }}
          >
            {tab.label}
          </Link>
        );
      })}

      {isGlobal && (
        <button
          onClick={handleGlobalToggle}
          style={{
            padding: "var(--space-2) var(--space-3)",
            borderRadius: "var(--radius-md)",
            border: `1px solid ${includeKr ? "var(--color-primary-500)" : "var(--color-border)"}`,
            background: includeKr ? "var(--color-primary-50)" : "#fff", // Light bg for active
            color: includeKr ? "var(--color-primary-700)" : "var(--color-neutral-900)",
            fontWeight: 800,
            fontSize: 16,
            cursor: "pointer",
            textAlign: "center",
            transition: "all var(--transition-fast)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "4px"
          }}
        >
          {includeKr ? "KR만 보기" : "전체 보기"}
        </button>
      )}

      {isLocal && (
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowCountryMenu(!showCountryMenu)}
            style={{
              width: "100%",
              padding: "var(--space-2) var(--space-3)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
              background: "#fff",
              color: "var(--color-neutral-900)",
              fontWeight: 800,
              fontSize: 16,
              cursor: "pointer",
              textAlign: "center",
              transition: "all var(--transition-fast)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px"
            }}
          >
            {country === "ALL" ? "국가 변경" : currentCountryLabel}

          </button>

          {showCountryMenu && (
            <>
              <div
                style={{ position: "fixed", inset: 0, zIndex: 90 }}
                onClick={() => setShowCountryMenu(false)}
              />
              <div style={{
                position: "absolute",
                top: "100%",
                right: 0,
                marginTop: "8px",
                background: "#fff",
                border: "1px solid var(--color-border)",
                borderRadius: "12px",
                boxShadow: "var(--shadow-lg)",
                width: "180px",
                maxHeight: "300px",
                overflowY: "auto",
                zIndex: 100,
                padding: "4px"
              }}>
                {countryOptions.map((opt) => (
                  <button
                    key={opt.code}
                    onClick={() => handleCountrySelect(opt.code)}
                    style={{
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 12px",
                      background: country === opt.code ? "var(--color-primary-50)" : "transparent",
                      color: country === opt.code ? "var(--color-primary-700)" : "var(--color-neutral-900)",
                      border: "none",
                      borderRadius: "8px",
                      fontSize: "16px",
                      fontWeight: 700,
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px"
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
