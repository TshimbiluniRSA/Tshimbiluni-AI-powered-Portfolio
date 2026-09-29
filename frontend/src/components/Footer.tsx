import { profile } from '../content/profile';
import { useResumeDownload } from '../hooks/useResumeDownload';
import { DownloadIcon, GitHubIcon, LinkedInIcon, MailIcon } from './icons';
import './Footer.css';

export default function Footer() {
  const { download, downloading, error } = useResumeDownload();
  const year = new Date().getFullYear();

  return (
    <>
      <section id="contact" className="section contact" aria-labelledby="contact-title">
        <div className="container contact__inner">
          <div>
            <span className="eyebrow">Contact</span>
            <h2 id="contact-title" className="section-title">
              Let&apos;s talk
            </h2>
            <p className="section-lead">
              I am interested in backend, full-stack and AI engineering roles where I can turn
              complex workflows into reliable software. Email is the fastest way to reach me.
            </p>
          </div>

          <div className="contact__actions">
            <a className="btn btn--primary" href={`mailto:${profile.links.email}`}>
              <MailIcon /> {profile.links.email}
            </a>
            <div className="contact__secondary">
              <a
                className="btn btn--secondary"
                href={profile.links.linkedin}
                target="_blank"
                rel="noopener noreferrer"
              >
                <LinkedInIcon /> LinkedIn
              </a>
              <a
                className="btn btn--secondary"
                href={profile.links.github}
                target="_blank"
                rel="noopener noreferrer"
              >
                <GitHubIcon /> GitHub
              </a>
              <button
                type="button"
                className="btn btn--secondary"
                onClick={download}
                disabled={downloading}
                aria-busy={downloading}
              >
                <DownloadIcon /> {downloading ? 'Preparing…' : 'Download CV'}
              </button>
            </div>
            {error && (
              <p className="form-error" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>
      </section>

      <footer className="site-footer">
        <div className="container site-footer__inner">
          <p>
            © {year} {profile.name}
          </p>
          <p>
            Built with React, FastAPI and PostgreSQL on AWS.{' '}
            <a
              href="https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio"
              target="_blank"
              rel="noopener noreferrer"
            >
              View source
            </a>
          </p>
        </div>
      </footer>
    </>
  );
}
