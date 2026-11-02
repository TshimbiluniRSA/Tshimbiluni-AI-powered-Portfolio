import type { CSSProperties } from 'react';
import { education, experience } from '../content/profile';
import './Experience.css';

export default function Experience() {
  return (
    <section id="experience" className="section" aria-labelledby="experience-title">
      <div className="grid experience">
        <h2 id="experience-title" className="experience__title" data-reveal>
          <span>Where I have</span> built software
        </h2>

        <div className="experience__table">
          <ul className="roles" aria-label="Roles">
            {experience.map((role, index) => (
              <li
                key={`${role.company}-${role.title}`}
                data-reveal
                style={{ '--i': index } as CSSProperties}
              >
                <details className="role" open={index === 0}>
                  <summary>
                    <span className="role__period muted">{role.period}</span>
                    <span className="role__title">{role.title}</span>
                    <span className="role__company">{role.company}</span>
                  </summary>
                  <div className="role__body">
                    <p className="small muted">{role.location}</p>
                    <ul>
                      {role.highlights.map((highlight) => (
                        <li key={highlight}>{highlight}</li>
                      ))}
                    </ul>
                  </div>
                </details>
              </li>
            ))}
          </ul>

          <ul className="roles roles--record" aria-label="Education and certifications" data-reveal>
            <li className="record">
              <span className="role__period muted">{education.year}</span>
              <span className="role__title">{education.degree}</span>
              <span className="role__company">{education.school}</span>
            </li>
            {education.certifications.map((certification) => {
              const [name, code] = certification.split(' (');
              return (
                <li key={certification} className="record">
                  <span className="role__period muted">Certified</span>
                  <span className="role__title">{name}</span>
                  <span className="role__company">{code?.replace(')', '')}</span>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </section>
  );
}
