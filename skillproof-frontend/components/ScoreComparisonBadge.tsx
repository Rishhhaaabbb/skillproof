// Task 14: Badge showing score delta between before and after analyses
interface ScoreComparisonBadgeProps {
  before?: number;
  after?: number;
}

export default function ScoreComparisonBadge({ before, after }: ScoreComparisonBadgeProps) {
  return (
    <span className="inline-block rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
      {before !== undefined && after !== undefined
        ? `${after - before > 0 ? '+' : ''}${(after - before).toFixed(1)}`
        : '--'}
      {/* Full implementation in Task 14 */}
    </span>
  );
}
