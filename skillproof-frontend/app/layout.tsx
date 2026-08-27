import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SkillProof',
  description: 'GitHub behavioral analysis and developer readiness verification',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
