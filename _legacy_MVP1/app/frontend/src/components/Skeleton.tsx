/**
 * Skeleton loading components for better perceived performance
 */

export function SkeletonText({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-zinc-200 dark:bg-zinc-800 rounded ${className}`}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <SkeletonText className="h-6 w-3/4 mb-2" />
          <SkeletonText className="h-4 w-1/2" />
        </div>
        <SkeletonText className="h-6 w-20" />
      </div>

      <div className="mb-6">
        <SkeletonText className="h-3 w-24 mb-2" />
        <SkeletonText className="h-12 w-full rounded-lg" />
      </div>

      <div className="border-t border-zinc-100 dark:border-zinc-800 pt-4">
        <SkeletonText className="h-4 w-32" />
      </div>
    </div>
  );
}

export function SkeletonTopicDetail() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section Skeleton */}
      <div className="mb-12">
        <SkeletonText className="h-4 w-32 mb-4" />
        <SkeletonText className="h-12 w-full mb-3" />
        <SkeletonText className="h-6 w-3/4" />
      </div>

      {/* Summary Section Skeleton */}
      <div className="mb-12 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 p-8">
        <SkeletonText className="h-4 w-32 mb-4" />
        <SkeletonText className="h-5 w-full mb-3" />
        <SkeletonText className="h-5 w-5/6 mb-3" />
        <SkeletonText className="h-5 w-4/6" />
        <div className="mt-6 flex gap-4">
          <SkeletonText className="h-4 w-24" />
          <SkeletonText className="h-4 w-24" />
        </div>
      </div>

      {/* Global Stance Skeleton */}
      <div className="mb-12 bg-white dark:bg-zinc-900 rounded-2xl border border-zinc-200 dark:border-zinc-800 p-8">
        <SkeletonText className="h-4 w-48 mb-6" />
        <SkeletonText className="h-12 w-full rounded-lg" />
      </div>

      {/* Country Cards Skeleton */}
      <div className="mb-12">
        <SkeletonText className="h-8 w-64 mb-6" />
        <div className="grid gap-6 md:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <SkeletonText className="h-8 w-8 rounded-full" />
                <div className="flex-1">
                  <SkeletonText className="h-5 w-32 mb-1" />
                  <SkeletonText className="h-3 w-20" />
                </div>
              </div>
              <SkeletonText className="h-12 w-full rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
