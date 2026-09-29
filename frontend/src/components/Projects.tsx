import { profile, projects } from '../content/profile';
import { useGitHubStats } from '../hooks/useGitHubStats';
import { ArrowUpRightIcon, GitHubIcon } from './icons';
import './Projects.css';

export default function Projects() {
  const { stats } = useGitHubStats();
  const languages = stats?.top_languages.slice(0, 4) ?? [];

  return (
    <section id="projects" className="section section--subtle" aria-labelledby="projects-title">
      <div className="container">
        <header className="section-header">
          <span className="eyebrow">Selected work</span>
          <h2 id="projects-title" className="section-title">
            Projects
          </h2>
          <p className="section-lead">
            What each project set out to solve, how it was built and what it achieved.
          </p>
        </header>

        <div className="project-grid">
          {projects.map((project) => (
            <article key={project.title} className="project-card">
              <div className="project-card__header">
                <span className="project-card__badge">{project.badge}</span>
                <h3 className="project-card__title">{project.title}</h3>
                <p className="project-card__summary">{project.summary}</p>
              </div>

              <dl className="project-card__story">
                <div>
                  <dt>Problem</dt>
                  <dd>{project.problem}</dd>
                </div>
                <div>
                  <dt>Approach</dt>
                  <dd>{project.approach}</dd>
                </div>
                <div>
                  <dt>Result</dt>
                  <dd>{project.result}</dd>
                </div>
              </dl>

              <ul className="tag-list" aria-label="Technologies">
                {project.tags.map((tag) => (
                  <li key={tag} className="tag">
                    {tag}
                  </li>
                ))}
              </ul>

              <div className="project-card__links">
                {project.live && (
                  <a href={project.live} target="_blank" rel="noopener noreferrer">
                    Live site <ArrowUpRightIcon />
                  </a>
                )}
                <a href={project.repo} target="_blank" rel="noopener noreferrer">
                  <GitHubIcon /> Source code
                </a>
              </div>
            </article>
          ))}
        </div>

        <div className="github-strip">
          <p>
            {languages.length > 0 ? (
              <>
                <span className="github-strip__label">Most used on GitHub:</span>{' '}
                {languages
                  .map((language) => `${language.name} ${language.percentage}%`)
                  .join(' · ')}
              </>
            ) : (
              'More of my code is on GitHub.'
            )}
          </p>
          <a href={profile.links.github} target="_blank" rel="noopener noreferrer">
            All repositories <ArrowUpRightIcon />
          </a>
        </div>
      </div>
    </section>
  );
}
