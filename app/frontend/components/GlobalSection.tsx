"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import type { GlobalItem } from "../lib/mock";

type Props = {
  items: GlobalItem[];
};

export function GlobalSection({ items }: Props) {
  const hero = items.slice(0, 3);
  const list = items.slice(3, 10);

  return (
    <section className="section">
      <div className="section-header">
        <h2>Global Insight</h2>
        <span className="chip chip-sky">Top 10</span>
      </div>

      <div className="stack gap-12">
        {hero.map((item, idx) => (
          <motion.article
            key={item.id}
            className="hero-card"
            initial={{ y: 24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: idx * 0.08 }}
          >
            <div className="hero-image">
              {item.hero_image_url ? (
                <Image
                  src={item.hero_image_url}
                  alt={item.title_ko}
                  fill
                  className="img-cover"
                  sizes="(max-width: 768px) 100vw, 600px"
                  priority={idx === 0}
                />
              ) : (
                <div className="hero-placeholder" />
              )}
              <div className="hero-gradient" />
            </div>
            <div className="hero-badges">
              <span className="chip chip-white">#{item.rank}</span>
              {item.hot_topic_badge ? (
                <span className="chip chip-amber">{item.hot_topic_badge}</span>
              ) : null}
              {item.is_pinned ? (
                <span className="chip chip-rose">PINNED</span>
              ) : null}
            </div>
            <div className="hero-text">
              {item.category ? (
                <p className="hero-category">{item.category}</p>
              ) : null}
              <h3>{item.title_ko}</h3>
            </div>
          </motion.article>
        ))}
      </div>

      <div className="stack">
        <h3 className="subheading">4~10위</h3>
        <div className="list-card">
          {list.map((item) => (
            <motion.article
              key={item.id}
              className="list-row"
              initial={{ y: 14, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true, margin: "0px 0px -40px 0px" }}
              transition={{ duration: 0.25, delay: (item.rank - 4) * 0.04 }}
            >
              <div className="rank-badge">{item.rank}</div>
              <div className="list-text">
                <p className="list-title">{item.title_ko}</p>
                <p className="list-keywords">{(item.keywords || []).join(" ")}</p>
              </div>
              {item.thumbnail_url ? (
                <div className="thumb">
                  <Image
                    src={item.thumbnail_url}
                    alt={item.title_ko}
                    fill
                    className="img-cover"
                    sizes="56px"
                  />
                </div>
              ) : null}
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
