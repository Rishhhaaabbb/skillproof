// Task 14: Shows before/after diff of analysis scores, skills, and resolved flags
import type { ComparisonResult } from '@/lib/types';

interface ComparisonDiffProps {
  comparison?: ComparisonResult;
}

export default function ComparisonDiff({ comparison }: ComparisonDiffProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Progress Comparison</h2>
      {comparison ? (
        <div className="mt-2 flex gap-8">
          <div>
            <p className="text-xs text-gray-500">Before</p>
            <p className="text-2xl font-bold">{comparison.before_readiness?.toFixed(0) ?? '--'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">After</p>
            <p className="text-2xl font-bold">{comparison.after_readiness?.toFixed(0) ?? '--'}</p>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-400">No comparison available</p>
      )}
      {/* Full implementation in Task 14 */}
    </div>
  );
}
