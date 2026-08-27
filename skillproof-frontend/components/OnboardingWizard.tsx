// Task 3: Multi-step onboarding wizard (GitHub username, first target role)
'use client';

interface OnboardingWizardProps {
  onComplete?: () => void;
}

export default function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  return (
    <div className="mx-auto max-w-lg rounded-lg border p-8">
      <h1 className="text-2xl font-semibold">Welcome to SkillProof</h1>
      <p className="mt-2 text-sm text-gray-600">Let's set up your profile.</p>
      {/* Full multi-step form implementation in Task 3 */}
    </div>
  );
}
