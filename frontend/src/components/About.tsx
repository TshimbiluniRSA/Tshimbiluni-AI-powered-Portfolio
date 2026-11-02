import type { CSSProperties } from 'react';
import { education, profile, skills } from '../content/profile';
import './About.css';

export default function About() {
  return (
    <section id="about" className="section" aria-labelledby="about-title">
      <div className="about">
        <h2 id="about-title" className="section-title about__title" data-reveal>
          Tools I use in production
        </h2>

        <dl className="about__facts" data-reveal>
          <div>
            <dt>Based in</dt>
            <dd>{profile.location}</dd>
          </div>
          <div>
            <dt>Studied</dt>
            <dd>
              {education.degree}, {education.school}, {education.year}
            </dd>
          </div>
          <div>
            <dt>Now</dt>
            <dd>
              {profile.current.title}, {profile.current.company}
            </dd>
          </div>
        </dl>

        <p className="about__paragraph" data-reveal style={{ '--i': 1 } as CSSProperties}>
          Most of my days are Python: Django REST Framework and FastAPI services, Celery workers and
          PostgreSQL, with React and TypeScript in front. I bring in language models where they earn
          their place, for document extraction, retrieval and assistants. I ship with Docker,
          Terraform and GitHub Actions on AWS and Azure, and I stay with a system after release.
        </p>

        <p className="about__word">Toolkit</p>
        <dl className="about__lists">
          {skills.map((group, index) => (
            <div key={group.area} data-reveal style={{ '--i': index } as CSSProperties}>
              <dt className="muted">{group.area}</dt>
              <dd>{group.items.join(', ')}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
