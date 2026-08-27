import { redirect } from 'next/navigation';

/**
 * Root page — redirects authenticated users to /dashboard,
 * unauthenticated users to /login.
 * Full auth check implemented in Task 3.
 */
export default function RootPage() {
  // TODO (Task 3): Check session/cookie and redirect conditionally
  redirect('/dashboard');
}
