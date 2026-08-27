// Task 6: GitHub-style 52-week contribution heatmap
interface ActivityHeatmapProps {
  heatmapData?: Record<string, number>;
}

export default function ActivityHeatmap({ heatmapData }: ActivityHeatmapProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Activity</h2>
      <p className="text-sm text-gray-500">
        {heatmapData ? Object.keys(heatmapData).length + ' days tracked' : 'No data'}
      </p>
      {/* Full implementation in Task 6 */}
    </div>
  );
}
