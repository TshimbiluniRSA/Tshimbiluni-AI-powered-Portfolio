import type { CSSProperties } from 'react';
import station from '../assets/photos/roodepoort-station-1896.jpg';
import { education, experience } from '../content/profile';
import './Experience.css';

export default function Experience() {
  return (
    <section id="experience" className="section" aria-labelledby="experience-title">
      <div className="grid experience">
        <h2 id="experience-title" className="experience__title" data-reveal>
          <span>Where I have</span> built software
        </h2>

        <figure className="experience__picture" data-reveal style={{ '--i': 2 } as CSSProperties}>
          <div className="experience__crop">
            <img
              src={station}
              alt="Railway staff and passengers on the platform of Roodepoort station beside a steam locomotive, about 1896"
              width={1536}
              height={991}
              loading="lazy"
              decoding="async"
            />
          </div>
          <figcaption className="small muted">Roodepoort station, about 1896</figcaption>
        </figure>

        <p className="experience__word small muted" aria-hidden="true">
          Roles
        </p>

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
