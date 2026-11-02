import { useState } from 'react';
import type { CSSProperties } from 'react';
import portrait from '../assets/photos/portrait.jpg';
import skyline from '../assets/photos/sandton-skyline.jpg';
import { profile } from '../content/profile';
import { useResumeDownload } from '../hooks/useResumeDownload';
import Header from './Header';
import './Hero.css';

const [firstName, lastName] = profile.name.split(' ');

export default function Hero() {
  const { download, downloading, error } = useResumeDownload();
  const [portraitFailed, setPortraitFailed] = useState(false);

  return (
    <section className="hero" aria-labelledby="hero-title" id="top">
      <Header />

      <figure className="hero__picture">
        <img
          src={skyline}
          alt="Sandton's towers above the trees of northern Johannesburg, seen from the west"
          width={1920}
          height={816}
          fetchPriority="high"
        />
      </figure>

      <div className="hero__row">
        <p className="hero__sentence">
          Software engineer in {profile.location}. I build Python backends and applied AI that run
          in production, today as a{' '}
          {profile.current.title.toLowerCase().replace('python', 'Python')} at{' '}
          {profile.current.company}.
        </p>
        <div className="hero__action">
          <button
            type="button"
            className="button"
            onClick={download}
            disabled={downloading}
            aria-busy={downloading}
          >
            {downloading ? 'Preparing CV…' : 'Download CV'}
          </button>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
        </div>
      </div>

      <h1 id="hero-title" className="hero__name">
        <span className="hero__line">
          <span data-line style={{ '--i': 0 } as CSSProperties}>
            {firstName}
          </span>
        </span>{' '}
        <span className="hero__line">
          <span data-line style={{ '--i': 1 } as CSSProperties}>
            {lastName}
            {!portraitFailed && (
              <img
                className="hero__portrait"
                src={portrait}
                alt=""
                width={460}
                height={460}
                onError={() => setPortraitFailed(true)}
              />
            )}
          </span>
        </span>
      </h1>
    </section>
  );
}
