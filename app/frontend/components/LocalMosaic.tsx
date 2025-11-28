"use client";

import React, { useEffect, useRef } from "react";
import Image from "next/image";
import { useInfiniteQuery } from "@tanstack/react-query";
import type { LocalItem, LocalListResponse } from "../lib/mock";

type Props = {
  initial: LocalListResponse;
};

export function LocalMosaic({ initial }: Props) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status, refetch } =
    useInfiniteQuery<LocalListResponse>({
      queryKey: ["local-trends"],
      queryFn: async ({ pageParam = 1 }) => {
        const res = await fetch(`/api/mock/local?page=${pageParam}`);
        if (!res.ok) throw new Error("failed");
        return (await res.json()) as LocalListResponse;
      },
      initialPageParam: 1,
      getNextPageParam: (lastPage) => (lastPage.hasNextPage ? lastPage.page + 1 : undefined),
      initialData: {
        pages: [initial],
        pageParams: [1]
      }
    });

  const items = data?.pages.flatMap((p) => p.items) ?? [];
  const sentinelIndex = Math.max(items.length - 3, 0);

  useEffect(() => {
    if (!hasNextPage) return;
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !isFetchingNextPage) {
            void fetchNextPage();
          }
        });
      },
      { rootMargin: "0px 0px 200px 0px" }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <section className="section">
      <div className="section-header">
        <h2>국가 트렌드</h2>
        <span className="chip chip-sky">KR · Infinite Scroll</span>
      </div>
      <div className="mosaic">
        {items.map((item, idx) => (
          <Tile
            key={item.topic_id}
            item={item}
            sentinelRef={idx === sentinelIndex ? sentinelRef : undefined}
          />
        ))}
      </div>
      <div className="load-zone">
        {isFetchingNextPage && <p className="status-text">불러오는 중...</p>}
        {status === "error" && (
          <button className="retry-btn" onClick={() => refetch()}>
            불러오기 실패. 다시 시도
          </button>
        )}
        {!hasNextPage && status === "success" && (
          <p className="status-text">더 이상 콘텐츠가 없습니다.</p>
        )}
      </div>
    </section>
  );
}

function Tile({
  item,
  sentinelRef
}: {
  item: LocalItem;
  sentinelRef?: React.RefObject<HTMLDivElement>;
}) {
  const sizeClass =
    item.display_level === 1
      ? "tile tile-lg"
      : item.display_level === 2
        ? "tile tile-md"
        : "tile tile-sm";

  return (
    <article className={sizeClass}>
      {sentinelRef ? (
        <div
          ref={sentinelRef}
          style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0 }}
        />
      ) : null}
      <div className="tile-media">
        {item.media_type === "IMAGE" && item.media_url ? (
          <Image
            src={item.media_url}
            alt={item.title}
            fill
            className="img-cover"
            sizes="(max-width: 768px) 50vw, 200px"
          />
        ) : item.media_type === "VIDEO" && item.media_url ? (
          <video
            className="video-cover"
            src={item.media_url}
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
          />
        ) : (
          <div className="tile-placeholder" />
        )}
      </div>
      <div className="tile-text">
        <p className="tile-keyword">#{item.keyword}</p>
        <p className="tile-title">{item.title}</p>
        <p className="tile-count">{item.article_count.toLocaleString()} articles</p>
      </div>
    </article>
  );
}
