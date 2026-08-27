// Task 1: Custom hook for polling background job status
'use client';

import { useEffect, useRef, useState } from 'react';
import api from '@/lib/api';
import type { JobStatus } from '@/lib/types';

interface UseJobPollerReturn {
  status: JobStatus['status'] | null;
  result: unknown;
  error: string | undefined;
  isLoading: boolean;
}

const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES: Array<JobStatus['status']> = ['complete', 'failed'];

/**
 * Polls GET /api/jobs/{jobId} every 3 seconds until the job reaches a
 * terminal state ('complete' or 'failed'), then stops automatically.
 *
 * @param jobId - UUID string of the background job, or null to do nothing.
 * @returns { status, result, error, isLoading }
 */
export function useJobPoller(jobId: string | null): UseJobPollerReturn {
  const [status, setStatus] = useState<JobStatus['status'] | null>(null);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  function clearPoller() {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  async function poll() {
    if (!jobId) return;
    try {
      const job = await api.get<JobStatus>(`/api/jobs/${jobId}`);
      setStatus(job.status);
      setResult(job.result ?? null);
      setError(job.error);

      if (TERMINAL_STATUSES.includes(job.status)) {
        setIsLoading(false);
        clearPoller();
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Failed to fetch job status';
      setError(message);
      setIsLoading(false);
      clearPoller();
    }
  }

  useEffect(() => {
    if (!jobId) {
      // Reset state when jobId is cleared
      setStatus(null);
      setResult(null);
      setError(undefined);
      setIsLoading(false);
      clearPoller();
      return;
    }

    setIsLoading(true);
    setStatus(null);
    setResult(null);
    setError(undefined);

    // Immediate first poll, then every POLL_INTERVAL_MS
    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      clearPoller();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  return { status, result, error, isLoading };
}
