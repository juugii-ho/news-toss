'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import SpectrumBar from './SpectrumBar';
import { ChevronDown, ChevronUp, ArrowRight } from 'lucide-react';
import { COUNTRY_FLAGS, COUNTRY_NAMES } from '@/lib/constants';
import { formatDisplayDate } from '@/lib/time';
import type { MegatopicCardProps } from '@/lib/types';

const MegatopicCard: React.FC<MegatopicCardProps> = ({ id, title, titleKr, date, articleCount, countriesInvolved, stats, summary }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    // Aggregate global stats for the main bar
    let globalSupportive = 0;
    let globalFactual = 0;
    let globalCritical = 0;

    Object.values(stats).forEach(s => {
        globalSupportive += s.supportive;
        globalFactual += s.factual;
        globalCritical += s.critical;
    });

    return (
        <article className="bg-white dark:bg-zinc-900 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 p-6 sm:p-8 hover:shadow-lg hover:border-zinc-300 dark:hover:border-zinc-700 transition-all duration-300 ease-out" aria-label={`메가토픽: ${titleKr || title}`}>
            <div className="flex justify-between items-start mb-4">
                <div className="flex flex-col gap-1.5">
                    {titleKr && (
                        <h3 className="text-xl sm:text-2xl font-bold text-zinc-900 dark:text-zinc-50 leading-tight font-serif">
                            {titleKr}
                        </h3>
                    )}
                    <h4 className={`text-sm sm:text-base text-zinc-500 dark:text-zinc-400 font-medium leading-relaxed ${!titleKr ? 'text-xl sm:text-2xl font-bold text-zinc-900 dark:text-zinc-50 leading-tight font-serif' : ''}`}>
                        {title}
                    </h4>
                    <div className="flex items-center gap-3 text-xs text-zinc-400 dark:text-zinc-500 mt-1.5">
                        <span>{formatDisplayDate(date)}</span>
                        <span className="text-zinc-300 dark:text-zinc-600">•</span>
                        <span className="font-medium">
                            <span className="text-zinc-600 dark:text-zinc-300">{articleCount}</span> articles
                        </span>
                    </div>
                </div>
                <span className="text-xs sm:text-sm font-medium text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-3 py-1.5 rounded-full whitespace-nowrap ml-3 flex-shrink-0 h-fit">
                    <span className="text-zinc-700 dark:text-zinc-200 font-semibold">{countriesInvolved.length}</span> countries
                </span>
            </div>

            {/* Why it matters */}
            {summary && (
                <div className="mb-6 pb-6 border-b border-zinc-100 dark:border-zinc-800">
                    <h4 className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
                        왜 중요한가
                    </h4>
                    <p className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">
                        {summary.length > 80 ? `${summary.substring(0, 80)}...` : summary}
                    </p>
                </div>
            )}

            <div className="mb-6">
                <div className="flex justify-between items-end mb-3">
                    <span className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Global Stance</span>
                </div>
                <SpectrumBar
                    supportive={globalSupportive}
                    factual={globalFactual}
                    critical={globalCritical}
                />
            </div>

            <div className="border-t border-zinc-100 dark:border-zinc-800 pt-4 space-y-3">
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="flex items-center justify-between w-full text-sm sm:text-base font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200 focus:outline-none focus:ring-2 focus:ring-zinc-400 rounded-lg px-2 transition-all min-h-[44px] py-2"
                    aria-expanded={isExpanded}
                    aria-controls={`country-breakdown-${id}`}
                    aria-label={`${countriesInvolved.length}개 국가별 분석 ${isExpanded ? '닫기' : '열기'}`}
                >
                    <span>Country Breakdown ({countriesInvolved.length})</span>
                    {isExpanded ? <ChevronUp size={18} aria-hidden="true" /> : <ChevronDown size={18} aria-hidden="true" />}
                </button>

                {isExpanded && (
                    <div id={`country-breakdown-${id}`} className="mt-4 grid grid-cols-1 gap-4 animate-in fade-in slide-in-from-top-2 duration-200" role="region" aria-label="국가별 상세 분석">
                        {countriesInvolved.map(code => {
                            const s = stats[code];
                            if (!s) return null;
                            return (
                                <div key={code} className="bg-zinc-50 dark:bg-zinc-800/50 rounded-lg p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="text-2xl" title={code}>{COUNTRY_FLAGS[code] || "🌐"}</span>
                                        <span className="text-sm sm:text-base font-medium text-zinc-700 dark:text-zinc-300">
                                            {COUNTRY_NAMES[code] || code}
                                        </span>
                                    </div>
                                    <SpectrumBar
                                        supportive={s.supportive}
                                        factual={s.factual}
                                        critical={s.critical}
                                    />
                                </div>
                            );
                        })}
                    </div>
                )}

                <Link
                    href={`/topics/${id}`}
                    className="group flex items-center justify-center gap-2 w-full text-sm sm:text-base font-medium text-zinc-900 dark:text-zinc-50 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:ring-offset-2 rounded-lg min-h-[44px] py-3 transition-all"
                    aria-label={`${titleKr || title} 전체 분석 보기`}
                >
                    View Full Analysis
                    <ArrowRight size={18} className="transition-transform duration-200 group-hover:translate-x-1" aria-hidden="true" />
                </Link>
            </div>
        </article>
    );
};

export default MegatopicCard;
