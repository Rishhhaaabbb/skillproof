// Task 6: Displays the Logistic Regression readiness score and confidence tier
interface LRScoreCardProps {
  lrScore?: number;
  confidenceLevel?: string;
}

export default function LRScoreCard({ lrScore, confidenceLevel }: LRScoreCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Readiness Score</h2>
      <p className="text-3xl font-bold">{lrScore ?? '--'}</p>
      {confidenceLevel && <p className="text-sm text-gray-500">{confidenceLevel} confidence</p>}
      {/* Full implementation in Task 6 */}
    </div>
  );
}
