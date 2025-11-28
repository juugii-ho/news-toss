'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { ExternalLink, Filter } from 'lucide-react';
import { COUNTRY_FLAGS, COUNTRY_NAMES } from '@/lib/constants';
import { fetchJSON } from '@/lib/api';
import type { Article, StanceType } from '@/lib/types';

interface RelatedArticlesProps {
  topicId: number;
  countriesInvolved: string[];
}

interface ArticlesResponse {
  data: Article[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasMore: boolean;
  };
}

export default function RelatedArticles({ topicId, countriesInvolved }: RelatedArticlesProps) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);
  const [selectedStance, setSelectedStance] = useState<StanceType | null>(null);

  // Intersection Observer for infinite scroll
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  // Fetch articles
  const fetchArticles = useCallback(async (pageNum: number, reset: boolean = false) => {
    try {
      if (reset) {
        setLoading(true);
        setArticles([]);
      } else {
        setLoadingMore(true);
      }

      const params = new URLSearchParams({
        page: String(pageNum),
        limit: '20',
      });

      if (selectedCountry) params.append('country', selectedCountry);
      if (selectedStance) params.append('stance', selectedStance);

      const response = await fetchJSON<ArticlesResponse>(
        `/api/topics/${topicId}/articles?${params.toString()}`,
        {},
        { maxRetries: 2, retryDelay: 1000 }
      );

      if (reset) {
        setArticles(response.data);
      } else {
        setArticles(prev => [...prev, ...response.data]);
      }

      setHasMore(response.pagination.hasMore);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load articles');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [topicId, selectedCountry, selectedStance]);

  // Initial load and filter changes
  useEffect(() => {
    setPage(1);
    fetchArticles(1, true);
  }, [fetchArticles]);

  // Infinite scroll observer
  useEffect(() => {
    if (!hasMore || loadingMore) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          const nextPage = page + 1;
          setPage(nextPage);
          fetchArticles(nextPage, false);
        }
      },
      { threshold: 0.1 }
    );

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observerRef.current.observe(currentRef);
    }

    return () => {
      if (observerRef.current && currentRef) {
        observerRef.current.unobserve(currentRef);
      }
    };
  }, [hasMore, loadingMore, page, fetchArticles]);

  // Get stance badge color
  const getStanceBadge = (stance: StanceType | null) => {
    if (!stance) return { color: 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400', label: 'Unknown' };

    switch (stance) {
      case 'supportive':
        return { color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400', label: 'Supportive' };
      case 'factual':
        return { color: 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400', label: 'Factual' };
      case 'critical':
        return { color: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400', label: 'Critical' };
      default:
        return { color: 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400', label: 'Unknown' };
    }
  };

  if (loading) {
    return (
      <div className="mb-12">
        <h3 className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-6 font-serif">
          Related Articles
        </h3>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 animate-pulse">
              <div className="h-4 w-3/4 bg-zinc-200 dark:bg-zinc-800 rounded mb-3" />
              <div className="h-3 w-1/4 bg-zinc-200 dark:bg-zinc-800 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-12">
        <h3 className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-6 font-serif">
          Related Articles
        </h3>
        <div className="bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl p-6 text-center">
          <p className="text-amber-900 dark:text-amber-200">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <section className="mb-12" aria-labelledby="related-articles-heading">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h3 id="related-articles-heading" className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-50 font-serif">
          Related Articles
        </h3>

        {/* Filters */}
        <div className="flex flex-wrap gap-2" role="group" aria-label="기사 필터">
          {/* Country Filter */}
          <label htmlFor="country-filter" className="sr-only">국가별 필터</label>
          <select
            id="country-filter"
            value={selectedCountry || ''}
            onChange={(e) => setSelectedCountry(e.target.value || null)}
            className="px-3 py-2 text-sm border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-400"
            aria-label="국가별 필터링"
          >
            <option value="">All Countries</option>
            {countriesInvolved.map((code) => (
              <option key={code} value={code}>
                {COUNTRY_FLAGS[code] || '🌐'} {COUNTRY_NAMES[code] || code}
              </option>
            ))}
          </select>

          {/* Stance Filter */}
          <label htmlFor="stance-filter" className="sr-only">스탠스별 필터</label>
          <select
            id="stance-filter"
            value={selectedStance || ''}
            onChange={(e) => setSelectedStance((e.target.value as StanceType) || null)}
            className="px-3 py-2 text-sm border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-400"
            aria-label="스탠스별 필터링"
          >
            <option value="">All Stances</option>
            <option value="supportive">Supportive</option>
            <option value="factual">Factual</option>
            <option value="critical">Critical</option>
          </select>
        </div>
      </div>

      {/* Articles List */}
      {articles.length === 0 ? (
        <div className="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-12 text-center">
          <p className="text-zinc-500 dark:text-zinc-400">No articles found with the selected filters.</p>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {articles.map((article) => {
              const stanceBadge = getStanceBadge(article.stance);

              return (
                <a
                  key={article.id}
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 hover:shadow-md transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50 mb-2 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors line-clamp-2">
                        {article.title_kr || article.title}
                      </h4>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-zinc-500 dark:text-zinc-400">
                        {article.country_code && (
                          <span className="flex items-center gap-1.5">
                            <span className="text-base">{COUNTRY_FLAGS[article.country_code] || '🌐'}</span>
                            <span>{COUNTRY_NAMES[article.country_code] || article.country_code}</span>
                          </span>
                        )}
                        {article.source && (
                          <>
                            <span>•</span>
                            <span>{article.source}</span>
                          </>
                        )}
                        {article.published_at && (
                          <>
                            <span>•</span>
                            <span>{new Date(article.published_at).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2 flex-shrink-0">
                      <ExternalLink className="w-5 h-5 text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors" />
                      {article.stance && (
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${stanceBadge.color}`}>
                          {stanceBadge.label}
                        </span>
                      )}
                    </div>
                  </div>
                </a>
              );
            })}
          </div>

          {/* Load More Trigger */}
          {hasMore && (
            <div ref={loadMoreRef} className="py-8 text-center">
              {loadingMore && (
                <div className="inline-flex items-center gap-2 text-sm text-zinc-500">
                  <div className="w-4 h-4 border-2 border-zinc-300 border-t-zinc-600 rounded-full animate-spin" />
                  <span>Loading more articles...</span>
                </div>
              )}
            </div>
          )}

          {!hasMore && articles.length > 0 && (
            <div className="py-8 text-center">
              <p className="text-sm text-zinc-500 dark:text-zinc-400">No more articles to load</p>
            </div>
          )}
        </>
      )}
    </section>
  );
}
