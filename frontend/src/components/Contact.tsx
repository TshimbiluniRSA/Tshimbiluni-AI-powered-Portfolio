import type { CSSProperties } from 'react';
import { profile } from '../content/profile';
import './Contact.css';

export default function Contact() {
  const [user, domain] = profile.links.email.split('@');

  return (
    <section id="contact" className="contact" aria-labelledby="contact-title">
      <h2 id="contact-title" className="contact__sentence" data-reveal>
        Hiring for backend, full-stack or AI engineering? Write to me.
      </h2>

      <a
        className="contact__email"
        href={`mailto:${profile.links.email}`}
        data-reveal
        style={{ '--i': 1 } as CSSProperties}
      >
        {user}
        <wbr />@{domain}
      </a>

      <div className="contact__corners">
        <p>{profile.location}, South Africa</p>
        <p className="contact__social">
          <a
            className="link"
            href={profile.links.linkedin}
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
          <a className="link" href={profile.links.github} target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </div>
    </section>
  );
}
