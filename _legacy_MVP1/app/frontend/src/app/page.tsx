'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import FeedCard from '@/components/FeedCard';
import { SkeletonCard } from '@/components/Skeleton';
import { fetchJSON } from '@/lib/api';
import { getRelativeTime } from '@/lib/time';
import { COUNTRY_FLAGS, COUNTRY_NAMES } from '@/lib/constants';
import type { TopicWithStats } from '@/lib/types';

export default function Home() {
    const [megatopics, setMegatopics] = useState<TopicWithStats[]>([]);
    const [nationalSections, setNationalSections] = useState<{ country: string; topics: TopicWithStats[] }[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [todayCount, setTodayCount] = useState<number>(0);

    useEffect(() => {
        const loadTopics = async () => {
            try {
                // Fetch more topics to allow for client-side filtering/grouping
                const data = await fetchJSON<{
                    meta?: { count: number; updatedAt: string };
                    data: TopicWithStats[];
                    fallback?: boolean
                }>(
                    '/api/topics?limit=500',
                    {},
                    { maxRetries: 2, retryDelay: 1000 }
                );

                if (data.fallback) throw new Error('API fallback');

                const allTopics = data.data || [];

                // 1. Separate Megatopics (>= 2 countries) vs National (1 country)
                const megas = allTopics.filter(t => t.countries_involved.length >= 2);
                const nationals = allTopics.filter(t => t.countries_involved.length === 1);

                // Top 10 Megatopics
                const topMegas = megas.slice(0, 10);
                setMegatopics(topMegas);

                // Overflow Megatopics (Rank 11+) -> Distribute to National Sections
                const overflowMegas = megas.slice(10);

                // IMPORTANT: Create a Set of Global Top 10 IDs to exclude from National sections
                const globalTopicIds = new Set(topMegas.map(t => t.id));

                // 2. Group National Topics by Country
                const grouped: Record<string, TopicWithStats[]> = {};

                // Add pure national topics (exclude if they're in Global Top 10)
                nationals.forEach(t => {
                    if (globalTopicIds.has(t.id)) return; // Skip if in Global Top 10
                    const code = t.countries_involved[0];
                    if (!grouped[code]) grouped[code] = [];
                    grouped[code].push(t);
                });

                // Add overflow megatopics to EACH involved country (also skip if in Global Top 10)
                overflowMegas.forEach(t => {
                    if (globalTopicIds.has(t.id)) return; // Skip if in Global Top 10
                    t.countries_involved.forEach(code => {
                        if (!grouped[code]) grouped[code] = [];
                        // Check for duplicates just in case, though IDs should be unique in source
                        if (!grouped[code].find(existing => existing.id === t.id)) {
                            grouped[code].push(t);
                        }
                    });
                });

                // 3. Sort Countries: KR, US, CN, JP, then Alphabetical
                const priorityOrder = ['KR', 'US', 'CN', 'JP'];
                const sortedCountries = Object.keys(grouped).sort((a, b) => {
                    const idxA = priorityOrder.indexOf(a);
                    const idxB = priorityOrder.indexOf(b);

                    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                    if (idxA !== -1) return -1;
                    if (idxB !== -1) return 1;

                    return a.localeCompare(b);
                });

                // 4. Create Sections (Top 3 per country, sorted by article count)
                const sections = sortedCountries.map(code => {
                    // Sort topics by article count (desc)
                    const sortedTopics = grouped[code].sort((a, b) => (b.article_count || 0) - (a.article_count || 0));
                    return {
                        country: code,
                        topics: sortedTopics.slice(0, 3)
                    };
                }).filter(s => s.topics.length > 0);

                setNationalSections(sections);

                // Meta info
                if (data.meta) {
                    setTodayCount(data.meta.count);
                    setLastUpdated(new Date(data.meta.updatedAt));
                } else if (allTopics.length > 0) {
                    const mostRecent = allTopics.reduce((latest, topic) => {
                        const topicDate = new Date(topic.date);
                        return topicDate > new Date(latest.date) ? topic : latest;
                    });
                    setLastUpdated(new Date(mostRecent.date));
                }

            } catch (err) {
                console.error('Failed to load topics', err);
            } finally {
                setLoading(false);
            }
        };

        loadTopics();
    }, []);

    return (
        <div className="min-h-screen bg-zinc-50 dark:bg-black flex flex-col">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md">
                <div className="mx-auto max-w-2xl px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Link href="/" className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:ring-offset-2 rounded-md px-2 py-1 -ml-2">
                            <span className="text-xl font-bold text-zinc-900 dark:text-zinc-50 font-serif">News Spectrum</span>
                            <span className="text-xs bg-zinc-900 text-white px-1.5 py-0.5 rounded text-[10px]">MVP</span>
                        </Link>
                        {lastUpdated && (
                            <div className="hidden sm:flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                <span>Updated {getRelativeTime(lastUpdated)}</span>
                            </div>
                        )}
                    </div>
                    <nav className="flex gap-4 text-sm font-medium text-zinc-600 dark:text-zinc-400">
                        <Link href="#" className="hover:text-zinc-900 dark:hover:text-zinc-50 hidden sm:inline">About</Link>
                    </nav>
                </div>
            </header>

            <main className="flex-grow w-full max-w-2xl mx-auto px-4 py-6 sm:py-8 space-y-12">

                {/* Global Megatopics Section */}
                <section>
                    <div className="mb-6 flex items-baseline justify-between">
                        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 font-serif">
                            Global Megatopics
                        </h2>
                        <span className="text-sm text-zinc-500 dark:text-zinc-400">Top 10</span>
                    </div>

                    {loading ? (
                        <div className="space-y-6">
                            {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
                        </div>
                    ) : megatopics.length > 0 ? (
                        <div className="space-y-6">
                            {megatopics.map((topic) => (
                                <FeedCard key={topic.id} topic={topic} />
                            ))}
                        </div>
                    ) : (
                        <p className="text-zinc-500">No global topics found.</p>
                    )}
                </section>

                {/* National Highlights Section */}
                {!loading && nationalSections.length > 0 && (
                    <section className="space-y-10">
                        <div className="border-t border-zinc-200 dark:border-zinc-800 pt-8">
                            <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50 font-serif mb-2">
                                National Highlights
                            </h2>
                            <p className="text-sm text-zinc-500 dark:text-zinc-400">
                                Top stories by country
                            </p>
                        </div>

                        {nationalSections.map((section) => (
                            <div key={section.country}>
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl" role="img" aria-label={COUNTRY_NAMES[section.country] || section.country}>
                                        {COUNTRY_FLAGS[section.country] || "🌐"}
                                    </span>
                                    <h3 className="text-lg font-bold text-zinc-800 dark:text-zinc-200">
                                        {COUNTRY_NAMES[section.country] || section.country}
                                    </h3>
                                </div>
                                <div className="space-y-4">
                                    {section.topics.map((topic) => (
                                        <FeedCard key={topic.id} topic={topic} />
                                    ))}
                                </div>
                            </div>
                        ))}
                    </section>
                )}

            </main>

            <footer className="border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 py-8 mt-auto">
                <div className="mx-auto max-w-2xl px-4 text-center text-sm text-zinc-500 dark:text-zinc-400">
                    <p>&copy; {new Date().getFullYear()} News Spectrum. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}
