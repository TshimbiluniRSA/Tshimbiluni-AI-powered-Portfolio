import { photoCredits, profile } from '../content/profile';
import './Footer.css';

const [firstName, lastName] = profile.name.split(' ');

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="site-footer__columns">
        <div>
          <p className="site-footer__head">On this page</p>
          <ul>
            <li>
              <a className="link" href="#work">
                Work
              </a>
            </li>
            <li>
              <a className="link" href="#experience">
                Experience
              </a>
            </li>
            <li>
              <a className="link" href="#assistant">
                Assistant
              </a>
            </li>
            <li>
              <a className="link" href="#contact">
                Contact
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="site-footer__head">Elsewhere</p>
          <ul>
            <li>
              <a
                className="link"
                href={profile.links.github}
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub
              </a>
            </li>
            <li>
              <a
                className="link"
                href={profile.links.linkedin}
                target="_blank"
                rel="noopener noreferrer"
              >
                LinkedIn
              </a>
            </li>
            <li>
              <a className="link" href={`mailto:${profile.links.email}`}>
                Email
              </a>
            </li>
          </ul>
        </div>
        <div>
          <p className="site-footer__head">This site</p>
          <p>
            React and TypeScript in front of FastAPI and PostgreSQL on AWS.{' '}
            <a
              className="link"
              href="https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio"
              target="_blank"
              rel="noopener noreferrer"
            >
              View the source
            </a>
          </p>
        </div>
        <div>
          <p className="site-footer__head">Photographs</p>
          <ul>
            {photoCredits.map((photo) => (
              <li key={photo.page}>
                <a className="link" href={photo.page} target="_blank" rel="noopener noreferrer">
                  {photo.what}
                </a>
                , {photo.credit}, {photo.license}, via Wikimedia Commons
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="site-footer__wordmark" aria-hidden="true">
        <span>{firstName}</span> <span>{lastName}</span>
      </p>
      <p className="site-footer__legal">
        © {year} {profile.name}
      </p>
    </footer>
  );
}
