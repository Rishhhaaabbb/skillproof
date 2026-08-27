// Task 6: Radar chart visualising multi-dimension skill breakdown using Recharts
interface SkillRadarChartProps {
  breakdown?: Record<string, number>;
}

export default function SkillRadarChart({ breakdown }: SkillRadarChartProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Skill Radar</h2>
      {/* Full Recharts RadarChart implementation in Task 6 */}
    </div>
  );
}
