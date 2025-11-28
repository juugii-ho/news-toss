import React from 'react';
import { getRelativeTime } from '@/lib/time';
import { ChevronDown } from 'lucide-react';

interface HeroProps {
    lastUpdated?: Date | null;
    todayCount?: number;
}

const Hero: React.FC<HeroProps> = ({ lastUpdated, todayCount = 0 }) => {
    // Format date as KST
    const formatKST = (date: Date) => {
        return date.toLocaleString('ko-KR', {
            timeZone: 'Asia/Seoul',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    return (
        <section className="relative bg-white dark:bg-zinc-950 py-20 sm:py-28 overflow-hidden border-b border-zinc-100 dark:border-zinc-800" role="region" aria-label="메인 히어로 섹션">
            <div className="mx-auto max-w-7xl px-6 lg:px-8 relative z-10">
                <div className="mx-auto max-w-3xl text-center">
                    {/* Meta Bar */}
                    <div className="mb-6 flex justify-center">
                        {lastUpdated && todayCount > 0 ? (
                            <div className="inline-flex flex-col sm:flex-row items-center gap-2 sm:gap-3 text-xs sm:text-sm text-zinc-600 dark:text-zinc-400">
                                <span className="font-medium">
                                    오늘 <span className="font-semibold text-zinc-900 dark:text-zinc-100">{todayCount}</span>개 토픽
                                </span>
                                <span className="hidden sm:inline text-zinc-300 dark:text-zinc-600">·</span>
                                <span className="flex items-center gap-1.5">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                    {formatKST(lastUpdated)} 업데이트
                                </span>
                                <span className="hidden sm:inline text-zinc-300 dark:text-zinc-600">·</span>
                                <span className="text-zinc-500 dark:text-zinc-500">G10 + CN/RU 커버</span>
                            </div>
                        ) : (
                            <span className="rounded-full px-4 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800">
                                Daily Intelligence Updates
                            </span>
                        )}
                    </div>
                    <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-6xl font-serif leading-tight">
                        5분 안에 오늘의 세계를 살펴보세요
                    </h1>
                    <p className="mt-6 text-lg sm:text-xl leading-relaxed text-zinc-600 dark:text-zinc-400">
                        핵심 이슈 3–5개, 각기 다른 시선까지 한눈에 담았습니다.
                    </p>
                    <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                        <a
                            href="#topics"
                            className="w-full sm:w-auto inline-flex items-center justify-center rounded-lg bg-zinc-900 px-6 py-3.5 text-base font-semibold text-white shadow-sm hover:bg-zinc-700 focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:ring-offset-2 transition-all dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200 dark:focus:ring-zinc-50 min-h-[44px]"
                            aria-label="오늘의 뉴스 목록으로 이동"
                        >
                            오늘의 뉴스 보기
                        </a>
                        <a
                            href="#"
                            className="text-base font-semibold text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-400 rounded px-3 py-2 transition-all min-h-[44px] flex items-center"
                            aria-label="News Spectrum 사용 방법 안내"
                        >
                            사용 방법 <span aria-hidden="true" className="ml-1">→</span>
                        </a>
                    </div>
                </div>
            </div>

            {/* Enhanced Scroll Indicator */}
            <a
                href="#topics"
                className="absolute bottom-6 left-1/2 transform -translate-x-1/2 text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-400 rounded-lg p-2 transition-all cursor-pointer group"
                aria-label="뉴스 목록으로 스크롤"
            >
                <div className="flex flex-col items-center gap-2">
                    <span className="text-xs font-medium uppercase tracking-wider">Scroll</span>
                    <ChevronDown className="w-6 h-6 animate-bounce group-hover:text-zinc-900 dark:group-hover:text-zinc-50 transition-colors" aria-hidden="true" />
                </div>
            </a>
        </section>
    );
};

export default Hero;
