// Task 8: Displays the user's current and longest coding streak
interface StreakCounterProps {
  currentStreak?: number;
  longestStreak?: number;
}

export default function StreakCounter({ currentStreak, longestStreak }: StreakCounterProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Streak</h2>
      <p className="text-2xl font-bold">{currentStreak ?? 0} days</p>
      <p className="text-sm text-gray-500">Best: {longestStreak ?? 0} days</p>
      {/* Full implementation in Task 8 */}
    </div>
  );
}
