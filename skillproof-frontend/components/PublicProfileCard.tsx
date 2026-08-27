// Task 13: Read-only public profile summary card for share links and /u/[username]
import type { User, Analysis } from '@/lib/types';

interface PublicProfileCardProps {
  user?: Partial<User>;
  analysis?: Partial<Analysis>;
}

export default function PublicProfileCard({ user, analysis }: PublicProfileCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">{user?.full_name ?? user?.github_username ?? 'Anonymous'}</h2>
      {user?.profile_headline && <p className="text-sm text-gray-600">{user.profile_headline}</p>}
      {analysis?.tpr_score !== undefined && (
        <p className="mt-2 text-sm">TPR: <strong>{analysis.tpr_score.toFixed(0)}</strong></p>
      )}
      {/* Full implementation in Task 13 */}
    </div>
  );
}
