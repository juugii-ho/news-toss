"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";
import type { LocalItem } from "../lib/mock";

type Props = {
  items: LocalItem[];
};

const MAX_ITEMS = 15;

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
        <span className="chip chip-sky">Prototype</span>
      </div>
      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: 380,
          aspectRatio: "360 / 520",
          margin: "0 auto",
          borderRadius: 20,
          border: "1px solid #e2e8f0",
          background: "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)",
          boxShadow: "0 10px 30px rgba(15,23,42,0.08)",
          overflow: "hidden"
        }}
      >
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
              boxShadow: "0 8px 20px rgba(15,23,42,0.12)",
              color: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexDirection: "column",
              padding: 8,
              cursor: "pointer",
              transform: "translateX(-50%)",
              overflow: "hidden"
            }}
            onClick={() => {
              // TODO: navigate to detail when routes are ready
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
      </div>
      <p className="status-text">
        초기 진입 시 우르르 떨어지는 연출만 재생합니다. 탭 시 팝 효과 후 상세 이동(추후 라우트 연결).
      </p>
    </section>
  );
}
