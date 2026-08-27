// Task 13: Form for recruiters to submit a contact request via a share token
'use client';

interface RecruiterRequestFormProps {
  shareToken: string;
  onSubmit?: (data: Record<string, string>) => void;
}

export default function RecruiterRequestForm({ shareToken, onSubmit }: RecruiterRequestFormProps) {
  return (
    <div className="rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Contact Candidate</h2>
      <p className="text-xs text-gray-400">Token: {shareToken}</p>
      {/* Full react-hook-form + zod implementation in Task 13 */}
    </div>
  );
}
