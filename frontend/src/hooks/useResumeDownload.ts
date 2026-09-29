import { useCallback, useState } from 'react';
import { api } from '../api/client';

/** Fetches a short-lived signed CV link from the API and starts the download. */
export function useResumeDownload() {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');

  const download = useCallback(async () => {
    setDownloading(true);
    setError('');
    try {
      const { download_url } = await api.cv.download();
      window.location.assign(download_url);
    } catch {
      setError('The CV could not be downloaded right now. Please try again shortly.');
    } finally {
      setDownloading(false);
    }
  }, []);

  return { download, downloading, error };
}
