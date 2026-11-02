import { useState } from 'react';
import type { CSSProperties } from 'react';
import portrait from '../assets/photos/portrait.jpg';
import { profile } from '../content/profile';
import { useResumeDownload } from '../hooks/useResumeDownload';
import Header from './Header';
import './Hero.css';

export default function Hero() {
  const { download, downloading, error } = useResumeDownload();
  const [portraitFailed, setPortraitFailed] = useState(false);

  return (
    <section className="hero" aria-labelledby="hero-title" id="top">
      <Header />

      <div className="hero__inner">
        <div className="hero__text">
          <h1
            id="hero-title"
            className="hero__name"
            data-load
            style={{ '--d': '80ms' } as CSSProperties}
          >
            {profile.name}
          </h1>
          <p className="hero__role" data-load style={{ '--d': '180ms' } as CSSProperties}>
            {profile.role}, {profile.focus.replace('&', 'and')}
          </p>
          <p className="hero__sentence" data-load style={{ '--d': '260ms' } as CSSProperties}>
            Based in {profile.location}. I build Python backends and applied AI that run in
            production, today as a {profile.current.title.toLowerCase().replace('python', 'Python')}{' '}
            at {profile.current.company}.
          </p>
          <div className="hero__actions" data-load style={{ '--d': '340ms' } as CSSProperties}>
            <button
              type="button"
              className="button"
              onClick={download}
              disabled={downloading}
              aria-busy={downloading}
            >
              {downloading ? 'Preparing CV…' : 'Download CV'}
            </button>
            <a className="link" href="#assistant">
              Ask my assistant
            </a>
          </div>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
        </div>

        {!portraitFailed && (
          <figure className="hero__portrait" data-load style={{ '--d': '200ms' } as CSSProperties}>
            <img
              src={portrait}
              alt={`Portrait of ${profile.name}`}
              width={460}
              height={460}
              fetchPriority="high"
              onError={() => setPortraitFailed(true)}
            />
          </figure>
        )}
      </div>
    </section>
  );
}
