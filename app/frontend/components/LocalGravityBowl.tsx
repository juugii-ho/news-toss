"use client";

import { useMemo, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import Matter, { Bodies, Body, Engine, Query, Runner, World } from "matter-js";
import type { LocalItem } from "../lib/mock";

type Props = {
  items: LocalItem[];
};

const MAX_ITEMS = 15;
const USE_MATTER = process.env.NEXT_PUBLIC_USE_MATTER === "true";

type Bubble = {
  id: string;
  size: number;
  color: string;
  x: number;
  delay: number;
  title: string;
  keyword: string;
};

const palette = ["#0EA5E9", "#F59E0B", "#EF4444", "#10B981", "#8B5CF6", "#F472B6", "#22D3EE"];

export function LocalGravityBowl({ items }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const engineRef = useRef<Engine | null>(null);
  const runnerRef = useRef<Runner | null>(null);
  const bodiesRef = useRef<Body[]>([]);

  const bubbles = useMemo<Bubble[]>(() => {
    const calcSize = (count: number) => {
      const min = 50;
      const max = 180;
      const normalized = Math.log(count + 1) / Math.log(5000);
      const size = min + (max - min) * normalized;
      return Math.min(Math.max(size, min), max);
    };

    return items.slice(0, MAX_ITEMS).map((item, idx) => ({
      id: item.topic_id,
      size: calcSize(item.article_count),
      color: palette[idx % palette.length],
      x: 10 + Math.random() * 80, // percent
      delay: idx * 0.05,
      title: item.title,
      keyword: item.keyword
    }));
  }, [items]);

  return (
    <section className="section">
      <div className="section-header">
        <h2>Gravity Issue Bowl (Lite)</h2>
        <span className="chip chip-sky">{USE_MATTER ? "Matter" : "Motion"} Prototype</span>
      </div>
      <div
        ref={containerRef}
        style={{
          position: "relative",
          width: "100%",
          maxWidth: 380,
          aspectRatio: "360 / 520",
          margin: "0 auto",
          borderRadius: 20,
          border: "1px solid #e2e8f0",
          background: "linear-gradient(160deg,#ffffff 0%,#f8fafc 100%)",
          boxShadow: "0 10px 30px rgba(15,23,42,0.08)",
          overflow: "hidden"
        }}
      >
        {USE_MATTER ? (
          <MatterBubbles
            canvasRef={canvasRef}
            bubbles={bubbles}
            containerRef={containerRef}
            engineRef={engineRef}
            runnerRef={runnerRef}
            bodiesRef={bodiesRef}
          />
        ) : (
          <MotionBubbles bubbles={bubbles} />
        )}
      </div>
      <p className="status-text">
        {USE_MATTER
          ? "Matter: 초기 3초 물리 시뮬 후 정지, 탭 시 짧게 튀김."
          : "Motion: 초기 드롭 애니메이션만 재생, 탭 팝 효과(추후 상세 이동)."}
      </p>
    </section>
  );
}

function MotionBubbles({ bubbles }: { bubbles: Bubble[] }) {
  return (
    <>
      {bubbles.map((bubble) => (
        <motion.button
          key={bubble.id}
          whileTap={{ scale: 1.05 }}
          initial={{ y: -260, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{
            delay: bubble.delay,
            type: "spring",
            stiffness: 140,
            damping: 14
          }}
          style={{
            position: "absolute",
            left: `${bubble.x}%`,
            top: "30%",
            width: bubble.size,
            height: bubble.size,
            borderRadius: "50%",
            background: bubble.color,
            border: "0",
            boxShadow: "0 12px 24px rgba(15,23,42,0.12), inset 0 4px 10px rgba(255,255,255,0.3)",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: 8,
            cursor: "pointer",
          transform: "translateX(-50%)",
          overflow: "hidden",
          backgroundImage:
              "radial-gradient(circle at 30% 30%, rgba(255,255,255,0.55), rgba(255,255,255,0.1) 45%, transparent 70%)"
        }}
      >
        <span style={{ fontSize: 12, fontWeight: 800, lineHeight: 1, textAlign: "center" }}>
          {bubble.keyword}
        </span>
          <span
            style={{
              fontSize: 11,
              lineHeight: 1.2,
              marginTop: 4,
              textAlign: "center",
              opacity: 0.8
            }}
          >
            {bubble.title.slice(0, 24)}
          </span>
        </motion.button>
      ))}
    </>
  );
}

function MatterBubbles({
  canvasRef,
  bubbles,
  containerRef,
  engineRef,
  runnerRef,
  bodiesRef
}: {
  canvasRef: React.RefObject<HTMLCanvasElement>;
  bubbles: Bubble[];
  containerRef: React.RefObject<HTMLDivElement>;
  engineRef: React.RefObject<Engine | null>;
  runnerRef: React.RefObject<Runner | null>;
  bodiesRef: React.RefObject<Body[]>;
}) {
  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const width = container.clientWidth || 360;
    const height = 520;

    const engine = Engine.create({ gravity: { x: 0, y: 1, scale: 0.001 } });
    const world = engine.world;
    engineRef.current = engine;

    // Walls
    const thickness = 60;
    const walls = [
      Bodies.rectangle(width / 2, height + thickness / 2, width, thickness, { isStatic: true }),
      Bodies.rectangle(-thickness / 2, height / 2, thickness, height * 2, { isStatic: true }),
      Bodies.rectangle(width + thickness / 2, height / 2, thickness, height * 2, { isStatic: true })
    ];
    World.add(world, walls);

    // Bodies
    bodiesRef.current = [];
    bubbles.forEach((bubble, idx) => {
          setTimeout(() => {
            const body = Bodies.circle(
              Math.random() * (width - bubble.size) + bubble.size / 2,
              -80 * idx,
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
      options: { width, height, wireframes: false, background: "#f8fafc" }
    });
    Matter.Render.run(render);

    const runner = Runner.create();
    runnerRef.current = runner;
    Runner.run(runner, engine);

    const timeout = setTimeout(() => {
      runner.enabled = false;
      bodiesRef.current.forEach((b) => Body.setStatic(b, true));
    }, 3600);

    return () => {
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
        setTimeout(() => {
          runner.enabled = false;
          Body.setStatic(hit, true);
        }, 1200);
      }
    };
    canvas.addEventListener("click", handleTap);
    canvas.addEventListener("touchstart", handleTap);
    return () => {
      canvas.removeEventListener("click", handleTap);
      canvas.removeEventListener("touchstart", handleTap);
    };
  }, []);

  return (
    <>
      <canvas ref={canvasRef} width={360} height={520} style={{ position: "absolute", inset: 0 }} />
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
