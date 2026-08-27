// Task 6: Displays the Technical Proficiency Rating score with sub-dimension breakdown
interface TPRScoreCardProps {
  tprScore?: number;
  breakdown?: Record<string, unknown>;
  flags?: string[];
}

export default function TPRScoreCard({ tprScore, breakdown, flags }: TPRScoreCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">TPR Score</h2>
      <p className="text-3xl font-bold">{tprScore ?? '--'}</p>
      {/* Full implementation in Task 6 */}
    </div>
  );
}
