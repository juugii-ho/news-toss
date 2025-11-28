'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { formatDisplayDate } from '@/lib/time';
import type { TopicWithStats, TopicCountryStats } from '@/lib/types';
import { Globe, MessageCircle, TrendingUp, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import SpectrumBar from './SpectrumBar';
import { getCountryFlag, getCountryName, getDefaultThumbnailUrl } from '@/lib/constants';
import { fetchJSON } from '@/lib/api';

interface FeedCardProps {
    topic: TopicWithStats;
}

interface TopicDetail extends TopicWithStats {
    stats: TopicCountryStats[];
    total_supportive: number;
    total_factual: number;
    total_critical: number;
}

const FeedCard: React.FC<FeedCardProps> = ({ topic }) => {
    const { id, title, title_kr, headline, date, article_count, countries_involved, thumbnail_url, divergence_score, summary } = topic;

    const [isExpanded, setIsExpanded] = useState(false);
    const [detailData, setDetailData] = useState<TopicDetail | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showAllCountries, setShowAllCountries] = useState(false);
    const [showAllArticles, setShowAllArticles] = useState(false);

    const displayTitle = headline || title_kr || title;
    const isHighDivergence = (divergence_score || 0) > 0.3; // Threshold for "High Conflict" badge
    const imageUrl = thumbnail_url || '/placeholders/globe.png';

    const handleToggleExpand = async () => {
        if (!isExpanded && !detailData) {
            // Fetch detail data on first expansion
            setLoading(true);
            setError(null);
            try {
                const data = await fetchJSON<{ data: TopicDetail }>(`/api/topics/${id}`);
                setDetailData(data.data);
                setIsExpanded(true);
            } catch (err) {
                console.error('Failed to fetch topic details:', err);
                setError('상세 정보를 불러오지 못했습니다. 다시 시도해주세요.');
                // Auto-clear error after 3 seconds
                setTimeout(() => setError(null), 3000);
            } finally {
                setLoading(false);
            }
        } else {
            setIsExpanded(!isExpanded);
        }
    };

    return (
        <article className="group bg-white dark:bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-300 hover:shadow-md">
            {/* Image Section */}
            <div className="relative aspect-[2/1] w-full overflow-hidden bg-gradient-to-br from-zinc-100 to-zinc-200 dark:from-zinc-800 dark:to-zinc-900">
                <Image
                    src={imageUrl}
                    alt={displayTitle}
                    fill
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    loading="lazy"
                />

                {/* Overlay Badge for High Divergence (The "Seasoning") */}
                {isHighDivergence && (
                    <div className="absolute top-3 right-3 bg-rose-500/90 backdrop-blur-sm text-white text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1 shadow-sm">
                        <TrendingUp size={12} />
                        <span>논쟁 중 🔥</span>
                    </div>
                )}
            </div>

            {/* Content Section */}
            <div className="p-5">
                {/* Meta Header */}
                <div className="flex items-center gap-2 text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">
                    <span className="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-zinc-600 dark:text-zinc-300">
                        {countries_involved.length}개국 반응
                    </span>
                    <span>•</span>
                    <span>{formatDisplayDate(date)}</span>
                </div>

                {/* Title */}
                <h3 className="text-lg sm:text-xl font-bold text-zinc-900 dark:text-zinc-50 leading-snug mb-3 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {displayTitle}
                    {!title_kr && (
                        <span className="text-xs text-zinc-500 ml-2" aria-label="English content">🇬🇧</span>
                    )}
                </h3>

                {/* Error Message */}
                {error && (
                    <div className="mt-4 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center justify-between gap-2">
                            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                            <button
                                onClick={handleToggleExpand}
                                className="text-xs font-semibold text-red-600 dark:text-red-400 hover:underline focus:outline-none focus:ring-2 focus:ring-red-500 rounded px-2 py-1"
                            >
                                재시도
                            </button>
                        </div>
                    </div>
                )}

                {/* Expanded Content */}
                {isExpanded && (
                    <div className="mt-6 space-y-6 animate-in fade-in slide-in-from-top-2 duration-300">
                        {loading ? (
                            <div className="text-center py-8">
                                <div className="inline-block w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                        ) : detailData ? (
                            <>
                                {/* What Happened Section */}
                                {detailData.summary && (
                                    <div className="pb-6 border-b border-zinc-100 dark:border-zinc-800">
                                        <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                                            💡 무슨 일이에요?
                                        </h4>
                                        <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
                                            {detailData.summary}
                                        </p>
                                    </div>
                                )}

                                {/* Global Stance */}
                                <div className="pb-6 border-b border-zinc-100 dark:border-zinc-800">
                                    <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                                        {countries_involved.length > 1 ? '🌍 전체 반응' : '📊 반응 분포'}
                                    </h4>
                                    <SpectrumBar
                                        supportive={detailData.total_supportive || 0}
                                        factual={detailData.total_factual || 0}
                                        critical={detailData.total_critical || 0}
                                    />
                                </div>

                                {/* Country Breakdown - Only for multi-country topics */}
                                {detailData.stats && detailData.stats.length > 0 && countries_involved.length > 1 && (
                                    <div className="pb-6 border-b border-zinc-100 dark:border-zinc-800">
                                        <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mb-3 flex items-center gap-1.5">
                                            <span>🗺️</span> 국가별 시선
                                        </h4>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            {detailData.stats
                                                .sort((a, b) => {
                                                    const totalA = a.supportive_count + a.factual_count + a.critical_count;
                                                    const totalB = b.supportive_count + b.factual_count + b.critical_count;
                                                    return totalB - totalA;
                                                })
                                                .slice(0, showAllCountries ? undefined : 4)
                                                .map((stat) => (
                                                    <div key={stat.id} className="bg-zinc-50 dark:bg-zinc-800/50 rounded-lg p-3 border border-zinc-100 dark:border-zinc-700/50">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <span className="text-xl">{getCountryFlag(stat.country_code)}</span>
                                                            <div className="flex-1 min-w-0">
                                                                <div className="flex items-center justify-between">
                                                                    <h5 className="text-xs font-bold text-zinc-900 dark:text-zinc-50 truncate">
                                                                        {getCountryName(stat.country_code)}
                                                                    </h5>
                                                                    <span className="text-[10px] text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-1.5 py-0.5 rounded-full">
                                                                        {stat.supportive_count + stat.factual_count + stat.critical_count}건
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <SpectrumBar
                                                            supportive={stat.supportive_count || 0}
                                                            factual={stat.factual_count || 0}
                                                            critical={stat.critical_count || 0}
                                                            avgScore={stat.avg_score ?? 0}
                                                        />
                                                    </div>
                                                ))}
                                        </div>
                                        {detailData.stats.length > 4 && (
                                            <button
                                                onClick={() => setShowAllCountries(!showAllCountries)}
                                                className="mt-3 w-full text-sm font-semibold text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-3 py-2"
                                            >
                                                {showAllCountries
                                                    ? '접기 ↑'
                                                    : `${detailData.stats.length - 4}개 국가 더 보기 ↓`
                                                }
                                            </button>
                                        )}
                                    </div>
                                )}

                                {/* Article Previews */}
                                {detailData.articles && detailData.articles.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 mb-3">
                                            📰 주요 기사 ({detailData.articles.length})
                                        </h4>
                                        <div className="space-y-2">
                                            {detailData.articles.slice(0, showAllArticles ? undefined : 3).map((article) => (
                                                <a
                                                    key={article.id}
                                                    href={article.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="block group/article bg-zinc-50 dark:bg-zinc-800/50 rounded-lg p-3 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                                                >
                                                    <div className="flex items-start justify-between gap-2">
                                                        <div className="flex-1 min-w-0">
                                                            <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 line-clamp-2 group-hover/article:text-blue-600 dark:group-hover/article:text-blue-400">
                                                                {article.title_kr || article.title}
                                                            </p>
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                                                                    {getCountryFlag(article.country_code || '')} {getCountryName(article.country_code || '')}
                                                                </span>
                                                            </div>
                                                        </div>
                                                        <ExternalLink size={14} className="flex-shrink-0 text-zinc-400 group-hover/article:text-blue-600 dark:group-hover/article:text-blue-400 transition-colors" />
                                                    </div>
                                                </a>
                                            ))}
                                        </div>
                                        {detailData.articles.length > 3 && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setShowAllArticles(!showAllArticles);
                                                }}
                                                className="mt-3 w-full text-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                                            >
                                                {showAllArticles ? '접기' : `기사 더보기 (${detailData.articles.length - 3}개 더)`}
                                            </button>
                                        )}
                                    </div>
                                )}
                            </>
                        ) : null}
                    </div>
                )}

                {/* Footer / Toggle Button */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
                    <div className="flex items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
                        <div className="flex items-center gap-1">
                            <MessageCircle size={14} />
                            <span>{article_count} articles</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <a
                            href={`/topics/${id}`}
                            className="text-xs font-semibold text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200 px-2 py-1 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                        >
                            전체 분석 보기
                        </a>
                        <button
                            onClick={handleToggleExpand}
                            className="text-xs font-semibold text-blue-600 dark:text-blue-400 flex items-center gap-1 hover:translate-x-1 transition-transform focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-2 py-1"
                            aria-expanded={isExpanded}
                            aria-label={isExpanded ? '접기' : '한 번에 보기'}
                        >
                            {isExpanded ? (
                                <>
                                    접기 <ChevronUp size={14} />
                                </>
                            ) : (
                                <>
                                    한 번에 보기 <ChevronDown size={14} />
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </article>
    );
};

export default FeedCard;
