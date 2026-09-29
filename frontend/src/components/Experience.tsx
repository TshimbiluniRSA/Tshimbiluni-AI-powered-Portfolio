import { education, experience } from '../content/profile';
import './Experience.css';

export default function Experience() {
  return (
    <section id="experience" className="section" aria-labelledby="experience-title">
      <div className="container">
        <header className="section-header">
          <span className="eyebrow">Experience</span>
          <h2 id="experience-title" className="section-title">
            Where I have built software
          </h2>
          <p className="section-lead">
            Production backends, AI integrations and cloud delivery across enterprise and product
            teams.
          </p>
        </header>

        <ol className="timeline">
          {experience.map((role) => (
            <li key={`${role.company}-${role.title}`} className="timeline__item">
              <div className="timeline__meta">
                <p className="timeline__period">{role.period}</p>
                <p className="timeline__location">{role.location}</p>
              </div>
              <div className="timeline__body">
                <h3 className="timeline__title">
                  {role.title}
                  <span className="timeline__company"> · {role.company}</span>
                </h3>
                <ul className="timeline__highlights">
                  {role.highlights.map((highlight) => (
                    <li key={highlight}>{highlight}</li>
                  ))}
                </ul>
              </div>
            </li>
          ))}
        </ol>

        <div className="education">
          <div>
            <h3 className="education__title">Education</h3>
            <p>
              {education.degree}, {education.school} ({education.year})
            </p>
          </div>
          <div>
            <h3 className="education__title">Certifications</h3>
            <p>{education.certifications.join(' · ')}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
