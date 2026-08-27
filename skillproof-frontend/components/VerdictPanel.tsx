// Task 9: Displays the adversarial evaluation verdict (skeptic vs advocate)
import type { EvaluationVerdict } from '@/lib/types';

interface VerdictPanelProps {
  verdict?: EvaluationVerdict;
}

export default function VerdictPanel({ verdict }: VerdictPanelProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Evaluation Verdict</h2>
      {verdict?.final_verdict ? (
        <p className="text-sm text-gray-700">{verdict.final_verdict}</p>
      ) : (
        <p className="text-sm text-gray-400">No verdict yet</p>
      )}
      {/* Full implementation in Task 9 */}
    </div>
  );
}
