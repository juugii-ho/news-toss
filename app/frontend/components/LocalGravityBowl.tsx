"use client";

import { useMemo, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Matter, { Bodies, Body, Engine, Query, Runner, World } from "matter-js";
import type { LocalItem } from "../lib/mock";
import { getCategoryIcon } from "@/lib/categories";

type Props = { items: LocalItem[]; showStatus?: boolean; countryName?: string; showHeader?: boolean };

type Bubble = {
  id: string;
  size: number;
  color: string;
  x: number;
  delay: number;
  title: string;
  keyword: string;
  image?: string | null;
  isGlobal?: boolean;
};

const MAX_ITEMS = 15;
const USE_MATTER = process.env.NEXT_PUBLIC_USE_MATTER === "true";
// Fallback palette for items without category
const fallbackPalette = [
  "#6366f1", // Indigo
  "#8b5cf6", // Violet
  "#ec4899", // Pink
  "#f59e0b", // Amber
  "#10b981", // Emerald
  "#3b82f6", // Blue
  "#14b8a6", // Teal
  "#f97316", // Orange
];

export function LocalGravityBowl({ items, showStatus = true, countryName = "대한민국", showHeader = true }: Props) {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const overlayRef = useRef<HTMLCanvasElement | null>(null);
  const engineRef = useRef<Matter.Engine | null>(null);
  const runnerRef = useRef<Matter.Runner | null>(null);
  const bodiesRef = useRef<Matter.Body[]>([]);
  const loadedImagesRef = useRef<Record<string, HTMLImageElement>>({});

  const bubbles = useMemo<Bubble[]>(() => {
    const calcSize = (count: number) => {
      const min = 45; // 원래 크기 복원
      const max = 180; // 10개 이상일 때 크게
      if (count >= 10) return max;
      // 작은 기사 수는 크게 안 부풀리되, 차이는 유지 (완만한 로그)
      const normalized = Math.log(count + 1) / Math.log(80); // count=2 → ~0.23, 5 → ~0.39, 9 → ~0.58
      const size = min + (max - min) * normalized * 0.6; // 완만하게
      return Math.min(Math.max(size, min), max);
    };
    return items.slice(0, MAX_ITEMS).map((item, idx) => {
      // Get category color if available
      const category = (item as any).category;
      const categoryInfo = getCategoryIcon(category);
      const color = category ? categoryInfo.color : fallbackPalette[idx % fallbackPalette.length];

      return {
        id: item.topic_id,
        size: calcSize(item.article_count),
        color: color,
        image: category ? categoryInfo.image : null,
        x: 10 + Math.random() * 80,
        delay: idx * 0.05,
        title: item.title,
        keyword: (item as any).is_global ? `🔥 ${item.keyword}` : item.keyword,
        isGlobal: (item as any).is_global === true
      };
    });
  }, [items]);

  const today = new Date();
  const dateStr = `${today.getMonth() + 1}월 ${today.getDate()}일`;

  const cleanCountryName = countryName.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, "").trim();

  return (
    <section className="section" style={{ gap: "var(--space-4)" }}>
      {showHeader && (
        <div className="section-header" style={{ justifyContent: "flex-start", gap: "8px", alignItems: "center" }}>
          <img src="/assets/Topic Bowl.png" alt="" width={28} height={28} style={{ objectFit: "contain" }} />
          <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.03em", margin: 0 }}>
            {dateStr} {cleanCountryName} Topic Bowl
          </h2>
        </div>
      )}
      <div
        ref={containerRef}
        style={{
          position: "relative",
          width: "100%",
          maxWidth: 380,
          aspectRatio: "360 / 520",
          margin: "0 auto",
          borderRadius: "var(--radius-xl)",
          background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
          overflow: "hidden",
          boxShadow: "var(--shadow-md)"
        }}
      >
        {USE_MATTER ? (
          <MatterBubbles
            bubbles={bubbles}
            canvasRef={canvasRef}
            overlayRef={overlayRef}
            containerRef={containerRef}
            engineRef={engineRef}
            runnerRef={runnerRef}
            bodiesRef={bodiesRef}
            onNavigate={(id) => router.push(`/local/${id}`)}
          />
        ) : (
          <MotionBubbles bubbles={bubbles} onNavigate={(id) => router.push(`/local/${id}`)} />
        )}
      </div>
      {showStatus ? (
        <p className="status-text">
          {USE_MATTER
            ? "Matter: 초기 5초 물리 시뮬 후 정지, 탭 시 짧게 튀김."
            : "Motion: 초기 드롭 애니메이션만 재생, 탭 팝 효과(추후 상세 이동)."}
        </p>
      ) : null}
    </section>
  );
}

function MotionBubbles({ bubbles, onNavigate }: { bubbles: Bubble[]; onNavigate: (id: string) => void }) {
  return (
    <>
      {bubbles.map((bubble) => (
        <motion.button
          key={bubble.id}
          whileTap={{ scale: 1.05 }}
          initial={{ y: -260, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: bubble.delay, type: "spring", stiffness: 140, damping: 14 }}
          style={{
            position: "absolute",
            left: `${bubble.x}%`,
            top: "30%",
            width: bubble.size,
            height: bubble.size,
            borderRadius: "50%",
            background: `linear-gradient(135deg, ${bubble.color} 0%, ${bubble.color}dd 100%)`,
            border: "2px solid rgba(255,255,255,0.3)",
            boxShadow: "0 8px 24px rgba(15,23,42,0.15), 0 4px 12px rgba(15,23,42,0.1), inset 0 2px 8px rgba(255,255,255,0.4)",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: 12,
            cursor: "pointer",
            transform: "translateX(-50%)",
            overflow: "hidden",
            transition: "all var(--transition-fast)"
          }}
          onClick={() => onNavigate(bubble.id)}
        >
          <span
            style={{
              fontSize: 14,
              fontWeight: 800,
              lineHeight: 1.2,
              textAlign: "center",
              textShadow: "0 2px 8px rgba(0,0,0,0.35), 0 1px 3px rgba(0,0,0,0.5)",
              whiteSpace: "pre-line",
              padding: "0 6px",
              letterSpacing: "-0.01em"
            }}
          >
            {bubble.keyword.replace(/\s+/g, "\n")}
          </span>
          <span
            style={{
              fontSize: 11,
              lineHeight: 1.3,
              marginTop: 6,
              textAlign: "center",
              opacity: 0.95,
              textShadow: "0 2px 8px rgba(0,0,0,0.35), 0 1px 3px rgba(0,0,0,0.5)",
              padding: "0 8px",
              whiteSpace: "pre-line",
              fontWeight: 600,
              maxWidth: "90%",
              overflow: "hidden",
              textOverflow: "ellipsis",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical"
            }}
          >
            {bubble.title.slice(0, 32)}
          </span>
          {bubble.isGlobal ? (
            <span
              style={{
                marginTop: 8,
                fontSize: 10,
                fontWeight: 800,
                padding: "4px 10px",
                borderRadius: "var(--radius-full)",
                background: "rgba(255,255,255,0.95)",
                color: "var(--color-primary-700)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                letterSpacing: "0.05em"
              }}
            >
              GLOBAL
            </span>
          ) : null}
        </motion.button>
      ))}
    </>
  );
}

function MatterBubbles({
  bubbles,
  canvasRef,
  overlayRef,
  containerRef,
  engineRef,
  runnerRef,
  bodiesRef,
  onNavigate
}: {
  bubbles: Bubble[];
  canvasRef: React.RefObject<HTMLCanvasElement>;
  overlayRef: React.RefObject<HTMLCanvasElement>;
  containerRef: React.RefObject<HTMLDivElement>;
  engineRef: React.MutableRefObject<Engine | null>;
  runnerRef: React.MutableRefObject<Runner | null>;
  bodiesRef: React.MutableRefObject<Body[]>;
  onNavigate: (id: string) => void;
}) {
  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    const overlay = overlayRef.current;
    if (!container || !canvas) return;

    const width = container.clientWidth || 360;
    const height = 560; // Increased from 520 to allow more space at bottom

    const engine = Engine.create({ gravity: { x: 0, y: 1, scale: 0.001 } });
    const world = engine.world;
    engineRef.current = engine;

    const thickness = 60;
    const walls = [
      Bodies.rectangle(width / 2, height - 30, width, thickness, { isStatic: true }), // Wall further down to fill bottom
      Bodies.rectangle(-thickness / 2, height / 2, thickness, height * 2, { isStatic: true }),
      Bodies.rectangle(width + thickness / 2, height / 2, thickness, height * 2, { isStatic: true })
    ];
    World.add(world, walls);

    bodiesRef.current = [];
    bubbles.forEach((bubble, idx) => {
      setTimeout(() => {
        const body = Bodies.circle(
          Math.random() * (width - bubble.size) + bubble.size / 2,
          -150 - (idx * 100), // Start further up to prevent top ghosting
          bubble.size / 2,
          {
            restitution: 0.72,
            friction: 0.06,
            frictionAir: 0.015,
            render: { fillStyle: bubble.color },
            label: bubble.id
          }
        );
        bodiesRef.current.push(body);
        World.add(world, body);
      }, idx * 80);
    });

    const render = Matter.Render.create({
      engine,
      canvas,
      options: {
        width,
        height,
        wireframes: false,
        background: "transparent"
      }
    });

    // Custom rendering function for better visuals
    let renderAnimId: number | null = null;
    const customRender = () => {
      const engine = engineRef.current;
      const canvas = canvasRef.current;
      const overlay = overlayRef.current;
      if (!engine || !canvas || !overlay) return;

      const ctx = canvas.getContext("2d");
      const overlayCtx = overlay.getContext("2d");
      if (!ctx || !overlayCtx) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      overlayCtx.clearRect(0, 0, overlay.width, overlay.height);

      // Draw gradient background
      const bgGradient = ctx.createLinearGradient(0, 0, width, height);
      bgGradient.addColorStop(0, "#f8fafc");
      bgGradient.addColorStop(1, "#f1f5f9");
      ctx.fillStyle = bgGradient;
      ctx.fillRect(0, 0, width, height);

      // Draw each bubble with gradient and shadow
      bodiesRef.current.forEach((body) => {
        const bubble = bubbles.find((b) => b.id === body.label);
        if (!bubble) return;

        const x = body.position.x;
        const y = body.position.y;
        const radius = bubble.size / 2;

        // Skip if off-screen
        if (y < -radius || y > height + radius) return;

        // Draw shadow
        ctx.save();
        ctx.shadowColor = "rgba(15, 23, 42, 0.15)";
        ctx.shadowBlur = 24;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 8;

        // Draw gradient circle
        const gradient = ctx.createLinearGradient(
          x - radius, y - radius,
          x + radius, y + radius
        );
        gradient.addColorStop(0, bubble.color);
        gradient.addColorStop(1, bubble.color + "dd");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Draw white border
        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.stroke();

        // Draw inner highlight
        ctx.save();
        const highlightGradient = ctx.createRadialGradient(
          x - radius * 0.3, y - radius * 0.3, 0,
          x, y, radius
        );
        highlightGradient.addColorStop(0, "rgba(255, 255, 255, 0.4)");
        highlightGradient.addColorStop(0.5, "rgba(255, 255, 255, 0.1)");
        highlightGradient.addColorStop(1, "transparent");
        ctx.fillStyle = highlightGradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      renderAnimId = requestAnimationFrame(customRender);
    };

    customRender();
    // Don't run Matter's default renderer - we're using custom rendering
    // Matter.Render.run(render);

    const runner = Runner.create();
    runnerRef.current = runner;
    Runner.run(runner, engine);

    // Overlay text rendering loop
    let animId: number | null = null;
    const drawOverlay = () => {
      if (!overlay) return;
      const ctx = overlay.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, overlay.width, overlay.height);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = "#ffffff";
      ctx.shadowColor = "rgba(0,0,0,0.4)";
      ctx.shadowBlur = 6;
      ctx.shadowOffsetY = 2;
      ctx.font = "800 15px -apple-system, BlinkMacSystemFont, 'Pretendard', 'Inter', sans-serif";

      bodiesRef.current.forEach((body) => {
        const bubble = bubbles.find((b) => b.id === body.label);
        if (!bubble) return;
        const x = Math.round(body.position.x);
        const y = Math.round(body.position.y);
        if (y < bubble.size * 0.3 || y > height + bubble.size) return; // 화면 밖이면 스킵해 잔상/떨림 방지
        const lines = bubble.keyword.split(/\s+/);
        const lineHeight = 16;
        const offsetY = -(lines.length - 1) * lineHeight * 0.5;
        lines.forEach((line, idx) => {
          ctx.fillText(line, x, y + offsetY + idx * lineHeight);
        });
      });
      animId = requestAnimationFrame(drawOverlay);
    };
    if (overlay) {
      overlay.width = width;
      overlay.height = height;
      drawOverlay();
    }

    const timeout = setTimeout(() => {
      runner.enabled = false;
      bodiesRef.current.forEach((b) => Body.setStatic(b, true));
    }, 7000);

    return () => {
      if (renderAnimId) cancelAnimationFrame(renderAnimId);
      if (animId) cancelAnimationFrame(animId);
      clearTimeout(timeout);
      Runner.stop(runner);
      Matter.Render.stop(render);
      Engine.clear(engine);
      bodiesRef.current = [];
    };
  }, [bubbles, canvasRef, containerRef, bodiesRef, engineRef, runnerRef]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const handleTap = (ev: MouseEvent | TouchEvent) => {
      const runner = runnerRef.current;
      const engine = engineRef.current;
      if (!runner || !engine) return;
      const rect = canvas.getBoundingClientRect();
      const clientX = "touches" in ev ? ev.touches[0].clientX : ev.clientX;
      const clientY = "touches" in ev ? ev.touches[0].clientY : ev.clientY;
      const point = { x: clientX - rect.left, y: clientY - rect.top };
      const hit = Query.point(bodiesRef.current, point)[0];
      if (hit) {
        runner.enabled = true;
        Body.setStatic(hit, false);
        Body.applyForce(hit, hit.position, { x: (Math.random() - 0.5) * 0.03, y: -0.04 });
        // 즉시 상세로 이동 (물리 효과는 짧게만)
        onNavigate(hit.label || "");
        setTimeout(() => {
          runner.enabled = false;
          Body.setStatic(hit, true);
        }, 600);
      }
    };
    canvas.addEventListener("click", handleTap);
    canvas.addEventListener("touchstart", handleTap);
    return () => {
      canvas.removeEventListener("click", handleTap);
      canvas.removeEventListener("touchstart", handleTap);
    };
  }, [onNavigate]);

  return (
    <>
      <canvas ref={canvasRef} width={360} height={560} style={{ position: "absolute", inset: 0 }} />
      <canvas
        ref={overlayRef}
        width={360}
        height={560}
        style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background: "linear-gradient(180deg, rgba(255,255,255,0.05), rgba(14,165,233,0.02))"
        }}
      />
    </>
  );
}
