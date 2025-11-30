"use client";

import { useState } from "react";
import { NewsConstellation } from "./NewsConstellation";
import { GlobalItem, LocalTopic } from "../lib/mock";

interface NewsConstellationSectionProps {
    items: GlobalItem[];
}

export function NewsConstellationSection({ items }: NewsConstellationSectionProps) {
    const [isOpen, setIsOpen] = useState(true);
    const [selectedItem, setSelectedItem] = useState<GlobalItem | LocalTopic | null>(null);

    return (
        <section className="mb-8">
            {/* Toss-style Header Card */}
            <div
                onClick={() => setIsOpen(!isOpen)}
                className="w-full bg-white active:scale-[0.98] transition-transform duration-200 ease-out cursor-pointer rounded-3xl p-5 shadow-sm border border-slate-100 flex items-center justify-between"
            >
                <div className="flex items-center gap-4">
                    {/* Colorful Icon Circle */}
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center flex-shrink-0">
                        <svg width="24" height="24" className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                        </svg>
                    </div>

                    <div className="flex flex-col">
                        <h2 className="text-xl font-extrabold text-slate-900 leading-tight">뉴스 별자리</h2>
                        <span className="text-sm text-slate-500 font-medium">
                            {isOpen ? "지구촌 이슈를 탐색하고 있어요" : "터치해서 이슈 지도를 펼쳐보세요"}
                        </span>
                    </div>
                </div>

                {/* Smooth Chevron */}
                <div className={`w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}>
                    <svg width="20" height="20" className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </div>

            {/* Content Container with Smooth Expansion */}
            <div
                className={`overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.4,0,0.2,1)] ${isOpen ? 'max-h-[1000px] opacity-100 mt-4' : 'max-h-0 opacity-0 mt-0'}`}
            >
                <div className="bg-white rounded-3xl p-1 border border-slate-100 shadow-sm">
                    <NewsConstellation items={items} onNodeClick={setSelectedItem} />

                    {/* Details Card (Integrated) */}
                    <div className={`transition-all duration-300 ${selectedItem ? 'h-auto opacity-100 p-5' : 'h-0 opacity-0 p-0 overflow-hidden'}`}>
                        {selectedItem && (
                            <div className="bg-slate-50 rounded-2xl p-5">
                                <div className="flex justify-between items-start mb-3">
                                    <div className="flex items-center gap-2">
                                        <span className={`text-[11px] font-bold px-2 py-1 rounded-[6px] ${'article_count' in selectedItem ? 'bg-blue-100 text-blue-600' : 'bg-emerald-100 text-emerald-600'}`}>
                                            {'article_count' in selectedItem ? 'GLOBAL ISSUE' : 'LOCAL TOPIC'}
                                        </span>
                                        {'country_code' in selectedItem && (
                                            <span className="text-xs text-slate-500 font-bold">{selectedItem.country_code}</span>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => setSelectedItem(null)}
                                        className="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-300 transition-colors"
                                    >
                                        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>

                                <h3 className="text-lg font-bold text-slate-900 mb-2 leading-snug">
                                    {'title_ko' in selectedItem ? selectedItem.title_ko : selectedItem.topic_name}
                                </h3>

                                <p className="text-sm text-slate-600 leading-relaxed font-medium">
                                    {'summary' in selectedItem ? selectedItem.summary : "해당 국가에서 화제가 되고 있는 로컬 뉴스입니다."}
                                </p>

                                {'localTopics' in selectedItem && selectedItem.localTopics && (
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        {selectedItem.localTopics.map((t: LocalTopic) => (
                                            <span key={t.id} className="text-[11px] font-bold px-2.5 py-1.5 bg-white border border-slate-200 rounded-[8px] text-slate-600 shadow-sm">
                                                {t.country_code} {t.topic_name}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                        {!selectedItem && (
                            <div className="text-center py-4 text-slate-400 text-sm font-medium">
                                별자리의 행성을 눌러 상세 내용을 확인해보세요
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}
