// Task 10: Displays matched and missing skills relative to a target role JD
interface GapAnalysisPanelProps {
  gapAnalysis?: {
    matched_skills?: string[];
    missing_skills?: string[];
    gap_description?: string;
    top_priorities?: string[];
  };
}

export default function GapAnalysisPanel({ gapAnalysis }: GapAnalysisPanelProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Gap Analysis</h2>
      {gapAnalysis?.gap_description && (
        <p className="text-sm text-gray-600">{gapAnalysis.gap_description}</p>
      )}
      {/* Full implementation in Task 10 */}
    </div>
  );
}
