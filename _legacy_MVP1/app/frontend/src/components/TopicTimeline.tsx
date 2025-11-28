'use client';

import { useEffect, useState } from 'react';
import { format } from 'date-fns';

interface HistoryRecord {
    id: string;
    date: string;
    title_en: string;
    title_kr?: string;
    drift_score: number | null;
    is_new_topic: boolean;
}

export default function TopicTimeline({ topicId }: { topicId: string }) {
    const [timeline, setTimeline] = useState<HistoryRecord[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchTimeline() {
            try {
                const res = await fetch(`/api/topics/${topicId}/timeline`);
                const data = await res.json();
                if (data.timeline) {
                    setTimeline(data.timeline);
                }
            } catch (e) {
                console.error("Failed to fetch timeline", e);
            } finally {
                setLoading(false);
            }
        }
        fetchTimeline();
    }, [topicId]);

    if (loading) return <div className="animate-pulse h-20 bg-gray-100 rounded-lg"></div>;
    if (timeline.length === 0) return null;

    return (
        <div className="mt-8 p-6 bg-white rounded-xl border border-gray-100 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Topic Timeline ⏳</h3>
            <div className="relative border-l-2 border-gray-200 ml-3 space-y-8">
                {timeline.map((record, idx) => {
                    const isLast = idx === timeline.length - 1;
                    const drift = record.drift_score || 0;

                    let badge = null;
                    if (record.is_new_topic) {
                        badge = <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">✨ New Topic</span>;
                    } else if (drift > 0.15) {
                        badge = <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-medium">🔥 Breaking Change</span>;
                    } else if (drift > 0.05) {
                        badge = <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full font-medium">📈 Evolving</span>;
                    } else {
                        badge = <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full font-medium">🔁 Ongoing</span>;
                    }

                    return (
                        <div key={record.id} className="relative pl-8">
                            {/* Dot */}
                            <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-white ${isLast ? 'bg-blue-600' : 'bg-gray-300'}`}></div>

                            <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-1">
                                <span className="text-sm text-gray-500 font-mono">{format(new Date(record.date), 'MMM d')}</span>
                                {badge}
                            </div>

                            <h4 className={`text-md ${isLast ? 'font-bold text-gray-900' : 'text-gray-600'}`}>
                                {record.title_kr || record.title_en}
                            </h4>

                            {/* Drift Score Debug (Optional) */}
                            {/* <div className="text-xs text-gray-400 mt-1">Drift: {drift.toFixed(4)}</div> */}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
