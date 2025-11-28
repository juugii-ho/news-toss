'use client';

import { useState } from 'react';
import { STANCE_EXPLANATIONS } from '@/lib/constants';
import type { SpectrumBarProps } from '@/lib/types';

export default function SpectrumBar({
  supportive,
  factual,
  critical,
  minVisiblePercent = 3,
  showExplanation = true,
  avgScore,
  height = "h-16 sm:h-12",
}: SpectrumBarProps) {
  const [hoveredStance, setHoveredStance] = useState<string | null>(null);
  const [tappedStance, setTappedStance] = useState<string | null>(null);
  const total = supportive + factual + critical;

  // Handle tap for mobile
  const handleStanceInteraction = (stance: string) => {
    if (tappedStance === stance) {
      setTappedStance(null);
    } else {
      setTappedStance(stance);
    }
  };

  const activeStance = tappedStance || hoveredStance;

  // Calculate percentages
  const supportivePct = total > 0 ? (supportive / total) * 100 : 0;
  const factualPct = total > 0 ? (factual / total) * 100 : 0;
  const criticalPct = total > 0 ? (critical / total) * 100 : 0;

  // Apply minimum visibility rule: any non-zero segment must be at least minVisiblePercent%
  const getVisiblePercent = (actualPct: number, value: number): number => {
    if (value === 0) return 0;
    return Math.max(actualPct, minVisiblePercent);
  };

  const supportiveVisible = getVisiblePercent(supportivePct, supportive);
  const factualVisible = getVisiblePercent(factualPct, factual);
  const criticalVisible = getVisiblePercent(criticalPct, critical);

  // Normalize to 100% for display
  const visibleTotal = supportiveVisible + factualVisible + criticalVisible;
  const supportiveDisplay = visibleTotal > 0 ? (supportiveVisible / visibleTotal) * 100 : 0;
  const factualDisplay = visibleTotal > 0 ? (factualVisible / visibleTotal) * 100 : 0;
  const criticalDisplay = visibleTotal > 0 ? (criticalVisible / visibleTotal) * 100 : 0;

  // Helper function to get score color and label
  const getScoreInfo = (score: number) => {
    if (score >= 67) return { color: 'text-emerald-600 dark:text-emerald-400', label: 'Supportive', bg: 'bg-emerald-50 dark:bg-emerald-950' };
    if (score >= 34) return { color: 'text-zinc-600 dark:text-zinc-400', label: 'Neutral', bg: 'bg-zinc-50 dark:bg-zinc-800' };
    return { color: 'text-amber-600 dark:text-amber-400', label: 'Critical', bg: 'bg-amber-50 dark:bg-amber-950' };
  };

  return (
    <div className="w-full space-y-3">
      {/* Spectrum Bar - taller on mobile for better touch targets */}
      <div className={`flex ${height} w-full overflow-hidden rounded-lg`}>
        {supportive > 0 && (
          <div
            className="bg-emerald-500 dark:bg-emerald-600 transition-all duration-300 cursor-pointer hover:brightness-110 active:brightness-125"
            style={{ width: `${supportiveDisplay}%` }}
            onMouseEnter={() => setHoveredStance('supportive')}
            onMouseLeave={() => setHoveredStance(null)}
            onClick={() => handleStanceInteraction('supportive')}
            role="button"
            tabIndex={0}
            aria-label={`Supportive: ${supportivePct.toFixed(1)}%`}
          />
        )}
        {factual > 0 && (
          <div
            className="bg-zinc-400 dark:bg-zinc-500 transition-all duration-300 cursor-pointer hover:brightness-110 active:brightness-125"
            style={{ width: `${factualDisplay}%` }}
            onMouseEnter={() => setHoveredStance('factual')}
            onMouseLeave={() => setHoveredStance(null)}
            onClick={() => handleStanceInteraction('factual')}
            role="button"
            tabIndex={0}
            aria-label={`Factual: ${factualPct.toFixed(1)}%`}
          />
        )}
        {critical > 0 && (
          <div
            className="bg-amber-500 dark:bg-amber-600 transition-all duration-300 cursor-pointer hover:brightness-110 active:brightness-125"
            style={{ width: `${criticalDisplay}%` }}
            onMouseEnter={() => setHoveredStance('critical')}
            onMouseLeave={() => setHoveredStance(null)}
            onClick={() => handleStanceInteraction('critical')}
            role="button"
            tabIndex={0}
            aria-label={`Critical: ${criticalPct.toFixed(1)}%`}
          />
        )}
      </div>

      {/* Stance Score Display (0-100) */}
      {avgScore !== undefined && (
        <div className="flex items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Stance Score:</span>
            <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${getScoreInfo(avgScore).bg}`}>
              <span className={`text-sm font-semibold ${getScoreInfo(avgScore).color}`}>
                {avgScore.toFixed(0)}
              </span>
              <span className={`text-xs font-medium ${getScoreInfo(avgScore).color}`}>
                / 100
              </span>
            </div>
          </div>
          <span className={`text-xs font-medium ${getScoreInfo(avgScore).color}`}>
            {getScoreInfo(avgScore).label}
          </span>
        </div>
      )}

      {/* Explanation - works with both hover and tap */}
      {showExplanation && activeStance && (
        <div className="text-sm sm:text-xs text-zinc-600 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-4 py-3 sm:px-3 sm:py-2 rounded-md animate-in fade-in slide-in-from-top-1 duration-200">
          <span className="font-semibold capitalize">{activeStance}:</span>{' '}
          {STANCE_EXPLANATIONS[activeStance as keyof typeof STANCE_EXPLANATIONS]}
        </div>
      )}

      {/* Legend with actual percentages - responsive sizing */}
      <div className="flex justify-between text-xs sm:text-sm gap-2">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div className="h-3 w-3 rounded-sm bg-emerald-500 dark:bg-emerald-600 flex-shrink-0" />
          <span className="text-zinc-700 dark:text-zinc-300 whitespace-nowrap">
            <span className="hidden sm:inline">Supportive </span>
            <span className="sm:hidden">Sup. </span>
            {supportivePct.toFixed(0)}%
          </span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div className="h-3 w-3 rounded-sm bg-zinc-400 dark:bg-zinc-500 flex-shrink-0" />
          <span className="text-zinc-700 dark:text-zinc-300 whitespace-nowrap">
            <span className="hidden sm:inline">Factual </span>
            <span className="sm:hidden">Fact. </span>
            {factualPct.toFixed(0)}%
          </span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div className="h-3 w-3 rounded-sm bg-amber-500 dark:bg-amber-600 flex-shrink-0" />
          <span className="text-zinc-700 dark:text-zinc-300 whitespace-nowrap">
            <span className="hidden sm:inline">Critical </span>
            <span className="sm:hidden">Crit. </span>
            {criticalPct.toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}
