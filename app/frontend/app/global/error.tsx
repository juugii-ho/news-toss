"use client";

export default function GlobalError({
  error,
  reset
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 8 }}>
      <h2 style={{ margin: 0 }}>문제가 발생했습니다</h2>
      <p style={{ margin: 0, color: "#555" }}>{error.message}</p>
      <button
        style={{
          padding: "8px 12px",
          borderRadius: 10,
          border: "1px solid #e5e7eb",
          fontWeight: 700,
          cursor: "pointer"
        }}
        onClick={() => reset()}
      >
        다시 시도
      </button>
    </div>
  );
}
