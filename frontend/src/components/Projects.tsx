import type { CSSProperties } from 'react';
import { projects } from '../content/profile';
import { LiveStats, ProjectVisual } from './ProjectVisuals';
import './Projects.css';

export default function Projects() {
  return (
    <section id="work" className="section work" aria-labelledby="work-title">
      <div className="grid">
        <h2 id="work-title" className="section-title work__title" data-reveal>
          Four systems I have built
        </h2>
      </div>

      {projects.map((project, index) => (
        <article
          key={project.id}
          className={`work__block work__block--${index + 1}`}
          aria-labelledby={`project-${project.id}`}
        >
          <div className="work__cluster">
            <h3
              id={`project-${project.id}`}
              className="work__name"
              data-reveal
              style={{ '--i': 2 } as CSSProperties}
            >
              {project.name}
            </h3>
            <div className="work__text" data-reveal style={{ '--i': 3 } as CSSProperties}>
              <p className="work__summary">{project.summary}</p>
              <dl className="work__story">
                <div>
                  <dt>Problem.</dt> <dd>{project.problem}</dd>
                </div>
                <div>
                  <dt>Approach.</dt> <dd>{project.approach}</dd>
                </div>
                <div>
                  <dt>Result.</dt> <dd>{project.result}</dd>
                </div>
              </dl>
              <p className="work__meta">
                {project.badge}. Built with {project.tags.join(', ')}.
              </p>
              <p className="work__links">
                {project.live && (
                  <a className="link" href={project.live} target="_blank" rel="noopener noreferrer">
                    Live site
                  </a>
                )}
                <a className="link" href={project.repo} target="_blank" rel="noopener noreferrer">
                  Source code
                </a>
              </p>
            </div>
            {project.id === 'portfolio' && (
              <div className="work__aside" data-reveal style={{ '--i': 1 } as CSSProperties}>
                <LiveStats />
              </div>
            )}
          </div>
          <div className="work__visual" data-reveal>
            <div className="work__field">
              <div className="work__frame">
                <ProjectVisual id={project.id} />
              </div>
            </div>
          </div>
        </article>
      ))}
    </section>
  );
}
