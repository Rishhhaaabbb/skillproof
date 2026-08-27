// Task 8: Grid of earned milestone badges
import type { Milestone } from '@/lib/types';

interface MilestoneBadgesProps {
  milestones?: Milestone[];
}

export default function MilestoneBadges({ milestones = [] }: MilestoneBadgesProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Milestones</h2>
      <p className="text-sm text-gray-500">{milestones.length} earned</p>
      {/* Full implementation in Task 8 */}
    </div>
  );
}
