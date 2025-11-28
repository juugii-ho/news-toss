'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import SpectrumBar from '@/components/SpectrumBar';
import RelatedArticles from '@/components/RelatedArticles';
import TopicTimeline from '@/components/TopicTimeline';
import { SkeletonTopicDetail } from '@/components/Skeleton';
import { fetchJSON } from '@/lib/api';
import { ArrowLeft } from 'lucide-react';
import { COUNTRY_FLAGS, COUNTRY_NAMES, CONTENT_LABELS } from '@/lib/constants';
import type { TopicWithStats, TopicCountryStats } from '@/lib/types';

type TopicDetail = TopicWithStats;

export default function TopicDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopic = async () => {
      try {
        // Fetch topic with retry logic
        const data = await fetchJSON<{ data: TopicDetail }>(
          `/api/topics/${params.id}`,
          {},
          { maxRetries: 2, retryDelay: 1000 }
        );
        setTopic(data.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchTopic();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black">
        <header className="sticky top-0 z-50 w-full border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md">
          <div className="mx-auto max-w-7xl px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-4 w-16 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold text-zinc-900 dark:text-zinc-50 font-serif">News Spectrum</span>
                <span className="text-xs bg-zinc-900 text-white px-1.5 py-0.5 rounded text-[10px]">MVP</span>
              </div>
            </div>
            <div className="h-4 w-32 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
          </div>
        </header>
        <SkeletonTopicDetail />
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-6">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-2">
            Topic Not Found
          </h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-4">
            {error || 'The requested topic could not be found.'}
          </p>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center gap-2 rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            <ArrowLeft size={16} />
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 transition-colors min-h-[44px] min-w-[44px] -ml-2 px-2"
            >
              <ArrowLeft size={18} />
              <span className="hidden sm:inline">Back</span>
            </button>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-zinc-900 dark:text-zinc-50 font-serif">News Spectrum</span>
              <span className="text-xs bg-zinc-900 text-white px-1.5 py-0.5 rounded text-[10px]">MVP</span>
            </div>
          </div>
          <div className="text-xs text-zinc-500">
            {new Date(topic.date).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="mb-12">
          <div className="mb-4">
            <span className="inline-block px-3 py-1 text-xs font-medium text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 rounded-full">
              글로벌 메가토픽
            </span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-zinc-900 dark:text-zinc-50 leading-tight font-serif mb-3">
            {topic.headline || topic.title_kr || topic.title}
          </h1>
          {(topic.headline || topic.title_kr) && (
            <h2 className="text-lg text-zinc-500 dark:text-zinc-400 font-medium">
              {topic.title}
            </h2>
          )}
        </div>

        {/* Summary Section */}
        <div className="mb-12 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 p-8">
          <div className="flex items-start justify-between gap-4 mb-4">
            <h3 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
              왜 중요한가
            </h3>
            <span className="text-xs text-zinc-400 dark:text-zinc-500 px-2 py-1 bg-zinc-50 dark:bg-zinc-800 rounded-md flex items-center gap-1 flex-shrink-0">
              <span className="opacity-60">🤖</span>
              {CONTENT_LABELS.AI_SUMMARY}
            </span>
          </div>
          <p className="text-lg text-zinc-700 dark:text-zinc-300 leading-relaxed">
            {topic.summary || `This global megatopic has been covered by ${topic.article_count} articles across ${topic.countries_involved.length} countries, showing diverse perspectives and international impact.`}
          </p>
          <div className="mt-6 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
              <span className="font-medium">{CONTENT_LABELS.SOURCES}:</span>
              <span>Based on <span className="font-semibold text-zinc-900 dark:text-zinc-100">{topic.article_count}</span> articles from <span className="font-semibold text-zinc-900 dark:text-zinc-100">{topic.countries_involved.length}</span> countries</span>
            </div>
          </div>
        </div>

        {/* Topic Timeline (Drift) */}
        <TopicTimeline topicId={String(topic.id)} />

        {/* Global Stance Overview */}
        <div className="mb-12 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 p-8">
          <h3 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-6">
            Global Stance Distribution
          </h3>
          <SpectrumBar
            supportive={topic.total_supportive}
            factual={topic.total_factual}
            critical={topic.total_critical}
          />
        </div>

        {/* Country-by-Country Breakdown */}
        <div className="mb-12">
          <h3 className="text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-zinc-50 mb-6 font-serif">
            Country-by-Country Analysis
          </h3>
          <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
            {topic.stats
              .sort((a, b) => {
                const totalA = a.supportive_count + a.factual_count + a.critical_count;
                const totalB = b.supportive_count + b.factual_count + b.critical_count;
                return totalB - totalA;
              })
              .map((stat) => (
                <div
                  key={stat.id}
                  className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 sm:p-8 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <span className="text-3xl sm:text-4xl">{COUNTRY_FLAGS[stat.country_code] || "🌐"}</span>
                    <div>
                      <h4 className="text-lg sm:text-xl font-semibold text-zinc-900 dark:text-zinc-50">
                        {COUNTRY_NAMES[stat.country_code] || stat.country_code}
                      </h4>
                      <p className="text-sm sm:text-base text-zinc-500">
                        {stat.supportive_count + stat.factual_count + stat.critical_count} articles
                      </p>
                    </div>
                  </div>
                  <SpectrumBar
                    supportive={stat.supportive_count}
                    factual={stat.factual_count}
                    critical={stat.critical_count}
                    avgScore={stat.avg_score}
                  />
                  {stat.summary && (
                    <p className="mt-4 text-base sm:text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">
                      {stat.summary}
                    </p>
                  )}
                </div>
              ))}
          </div>
        </div>

        {/* Related Articles */}
        <RelatedArticles
          topicId={topic.id}
          countriesInvolved={topic.countries_involved}
        />
      </main>
    </div>
  );
}
