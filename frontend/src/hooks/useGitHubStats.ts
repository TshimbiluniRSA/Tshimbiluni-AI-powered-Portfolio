import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { GitHubStats } from '../api/client';

let cachedStats: GitHubStats | null = null;
let statsRequest: Promise<GitHubStats> | null = null;

function loadStats() {
  if (cachedStats) return Promise.resolve(cachedStats);
  if (!statsRequest) {
    statsRequest = api.github.getStats().then((stats) => {
      cachedStats = stats;
      return stats;
    }).finally(() => { statsRequest = null; });
  }
  return statsRequest;
}

/** Shares one GitHub-stat request and its last successful result across consumers. */
export function useGitHubStats() {
  const [stats, setStats] = useState<GitHubStats | null>(cachedStats);
  const [loading, setLoading] = useState(!cachedStats);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    loadStats()
      .then((result) => { if (active) setStats(result); })
      .catch(() => { if (active) setError(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return { stats, loading, error };
}
