import { useState } from 'react';
import { profile } from '../content/profile';
import { useResumeDownload } from '../hooks/useResumeDownload';
import { DownloadIcon, GitHubIcon, LinkedInIcon, MailIcon, MapPinIcon } from './icons';
import './Hero.css';

export default function Hero() {
  const { download, downloading, error } = useResumeDownload();
  const [avatarFailed, setAvatarFailed] = useState(false);

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="container hero__inner">
        <div className="hero__content">
          <p className="hero__status">
            <span className="hero__status-dot" aria-hidden="true" />
            {profile.current.title} at {profile.current.company}
          </p>

          <h1 id="hero-title" className="hero__title">
            {profile.name}
          </h1>
          <p className="hero__role">
            {profile.role} <span aria-hidden="true">·</span> {profile.focus}
          </p>
          <p className="hero__summary">{profile.summary}</p>

          <div className="hero__actions">
            <button
              type="button"
              className="btn btn--primary"
              onClick={download}
              disabled={downloading}
              aria-busy={downloading}
            >
              <DownloadIcon />
              {downloading ? 'Preparing CV…' : 'Download CV'}
            </button>
            <a href="#assistant" className="btn btn--secondary">
              Ask my AI assistant
            </a>
          </div>
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <ul className="hero__links" aria-label="Contact and profiles">
            <li>
              <a href={profile.links.github} target="_blank" rel="noopener noreferrer">
                <GitHubIcon /> GitHub
              </a>
            </li>
            <li>
              <a href={profile.links.linkedin} target="_blank" rel="noopener noreferrer">
                <LinkedInIcon /> LinkedIn
              </a>
            </li>
            <li>
              <a href={`mailto:${profile.links.email}`}>
                <MailIcon /> {profile.links.email}
              </a>
            </li>
            <li className="hero__location">
              <MapPinIcon /> {profile.location}
            </li>
          </ul>
        </div>

        <div className="hero__portrait">
          {avatarFailed ? (
            <div className="hero__avatar hero__avatar--fallback" aria-hidden="true">
              TN
            </div>
          ) : (
            <img
              className="hero__avatar"
              src={profile.avatarUrl}
              alt={`Portrait of ${profile.name}`}
              width={320}
              height={320}
              onError={() => setAvatarFailed(true)}
            />
          )}
        </div>
      </div>
    </section>
  );
}
