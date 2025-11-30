"use client";

import React, { useEffect, useRef } from "react";
import Image from "next/image";
import { useInfiniteQuery } from "@tanstack/react-query";
import Link from "next/link";
import type { LocalItem, LocalListResponse } from "../lib/mock";
import { LocalTile } from "./LocalTile";

type Props = {
  initial?: LocalListResponse;
  country: string;
  className?: string;
  viewMode?: "grid" | "list";
};

export function LocalMosaic({ initial, country, className, style, viewMode = "list" }: Props) {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, status, refetch } =
    useInfiniteQuery<LocalListResponse>({
      queryKey: ["local-trends", country],
      queryFn: async ({ pageParam = 1 }) => {
        const res = await fetch(`/api/local/trends?page=${pageParam}&country=${country}`);
        if (!res.ok) throw new Error("failed");
        return (await res.json()) as LocalListResponse;
      },
      initialPageParam: 1,
      getNextPageParam: (lastPage) => (lastPage.hasNextPage ? lastPage.page + 1 : undefined),
      initialData: initial
        ? {
          pages: [initial],
          pageParams: [1]
        }
        : undefined
    });

  const items = data?.pages.flatMap((p) => p.items) ?? [];
  const safeItems = items.filter((i) => i && (i as any).topic_id);
  const sentinelIndex = Math.max(safeItems.length - 3, 0);

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
    <section className={`section ${className || ""}`} style={style}>
      {safeItems.length === 0 ? (
        <p className="status-text">아직 불러올 뉴스가 없습니다.</p>
      ) : (
        <div className={viewMode === "grid" ? "mosaic" : "stack gap-12"}>
          {safeItems.map((item, idx) => (
            <LocalTile
              key={item.topic_id}
              item={item}
              viewMode={viewMode}
              sentinelRef={idx === sentinelIndex ? sentinelRef : undefined}
            />
          ))}
        </div>
      )}
      <div className="load-zone">
        {isFetchingNextPage && <p className="status-text">불러오는 중...</p>}
        {status === "error" && (
          <button className="retry-btn" onClick={() => refetch()}>
            불러오기 실패. 다시 시도
          </button>
        )}
      </div>
    </section>
  );
}
