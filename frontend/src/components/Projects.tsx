import React, { useEffect, useState } from 'react';
import './Projects.css';
import { api } from '../api/client';
import { useInView } from '../hooks/useInView';

interface Project {
  id: number;
  name: string;
  description?: string;
  language?: string;
  topics?: string[];
  stars?: number;
  forks?: number;
  html_url: string;
}

interface CuratedProject {
  title: string;
  category: string;
  languageOverride: string;
  description: string;
  value: string;
  tags: string[];
  featured: boolean;
  status: 'Production' | 'Prototype' | 'Learning Project';
}

interface DisplayProject extends CuratedProject {
  repoKey: string;
  html_url: string;
  stars?: number;
  forks?: number;
  hasLiveData: boolean;
}

const curatedProjects: Record<string, CuratedProject> = {
  'Tshimbiluni-AI-powered-Portfolio': {
    title: 'AI-Powered Developer Portfolio',
    category: 'Full-stack Portfolio',
    languageOverride: 'React + FastAPI',
    description:
      'A production-deployed personal portfolio built with React, TypeScript, FastAPI, PostgreSQL, and AI integration. It presents my work and career direction while demonstrating frontend design, backend APIs, database integration, AI features, and deployment on Render.',
    value:
      'Shows my ability to connect frontend, backend, database, AI services, and deployment into one working full-stack application.',
    tags: ['React', 'TypeScript', 'FastAPI', 'Python', 'PostgreSQL', 'AI Integration', 'Render', 'Docker'],
    featured: true,
    status: 'Production',
  },
  'Context-Window-Aware-RAG-Deloitte-assessment-': {
    title: 'Context Window Aware RAG Assessment',
    category: 'RAG Experiment',
    languageOverride: 'Python',
    description:
      'A retrieval-augmented generation project focused on working within context-window limits and structuring information for AI-assisted answers.',
    value:
      'Demonstrates practical LLM application design, retrieval workflows, prompt structure, and AI evaluation thinking.',
    tags: ['Python', 'RAG', 'LLMs', 'AI Engineering', 'Retrieval'],
    featured: false,
    status: 'Prototype',
  },
  'BuildwithAI-buildathon': {
    title: 'Build with AI Buildathon',
    category: 'AI Prototype',
    languageOverride: 'TypeScript',
    description:
      'A buildathon project exploring how AI can be used inside a working application experience rather than remaining as a standalone prompt demo.',
    value:
      'Shows rapid prototyping speed, frontend implementation, and experimentation with AI-enabled product ideas under time pressure.',
    tags: ['TypeScript', 'React', 'AI Prototype', 'Product Thinking'],
    featured: false,
    status: 'Prototype',
  },
  'Blog-Project-Tshimbiluni': {
    title: 'Personal Blog Project',
    category: 'Frontend Practice',
    languageOverride: 'TypeScript',
    description:
      'A blog-style project used to practise frontend structure, routing, content presentation, and reusable UI patterns.',
    value:
      'Shows continued frontend learning, component composition, and content-focused application building outside of work projects.',
    tags: ['TypeScript', 'React', 'Frontend', 'UI'],
    featured: false,
    status: 'Learning Project',
  },
};

function buildDisplayProjects(fetched: Project[]): DisplayProject[] {
  return Object.entries(curatedProjects)
    .map(([repoKey, curated]) => {
      const match = fetched.find((project) => project.name.toLowerCase() === repoKey.toLowerCase());

      return {
        ...curated,
        repoKey,
        html_url: match?.html_url || `https://github.com/TshimbiluniRSA/${repoKey}`,
        stars: match?.stars,
        forks: match?.forks,
        hasLiveData: Boolean(match),
      };
    })
    .sort((a, b) => Number(b.featured) - Number(a.featured));
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<DisplayProject[]>(() => buildDisplayProjects([]));
  const [loading, setLoading] = useState(true);
  const { ref, isInView } = useInView<HTMLElement>();

  useEffect(() => {
    (async () => {
      let fetchedProjects: Project[] = [];

      try {
        fetchedProjects = await api.repositories.getFeatured();
      } catch (error) {
        console.error('Failed to fetch projects:', error);

        try {
          const data = await api.repositories.getByUsername('TshimbiluniRSA', 1, 6);
          fetchedProjects = data.items || [];
        } catch (fallbackError) {
          console.error('Fallback fetch failed:', fallbackError);
        }
      } finally {
        setProjects(buildDisplayProjects(fetchedProjects));
        setLoading(false);
      }
    })();
  }, []);

  const renderableProjects = projects.length >= 3 ? projects : projects.filter((project) => project.featured);
  const showMoreWriteupsNote = projects.length < 3;

  return (
    <section id="projects" className="projects" ref={ref}>
      <div className="container">
        <p className="section-kicker">Case Studies</p>
        <h2 className={`section-title reveal ${isInView ? 'is-visible' : ''}`}>Selected Work</h2>
        <p className="section-subtitle">
          Selected work that shows how I connect frontend, backend, AI workflows, databases, and deployment into practical software.
        </p>
        {loading ? (
          <p className="loading">Loading projects...</p>
        ) : (
          <>
            <div className="projects-grid">
              {renderableProjects.map((project, index) => (
                <article
                  key={project.repoKey}
                  className={`project-card ${project.featured ? 'featured' : 'standard'} reveal ${isInView ? 'is-visible' : ''}`}
                  style={{ '--reveal-delay': `${index * 0.08}s` } as React.CSSProperties}
                >
                  <div className="project-card-header">
                    <div>
                      <span className="project-category">{project.category}</span>
                      <span className="project-status">{project.status}</span>
                    </div>
                    <em>{project.languageOverride}</em>
                  </div>
                  <h3 className="project-title">{project.title}</h3>
                  <p className="project-description">{project.description}</p>
                  <p className="project-value">{project.value}</p>
                  <div className="project-technologies">
                    {project.tags.map((tag) => (
                      <span key={tag} className="tech-tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="project-footer">
                    {project.hasLiveData && (
                      <span className="project-stats">
                        ⭐ {project.stars || 0} · 🍴 {project.forks || 0}
                      </span>
                    )}
                    <a href={project.html_url} target="_blank" rel="noopener noreferrer" className="project-link">
                      View on GitHub →
                    </a>
                  </div>
                </article>
              ))}
            </div>
            {showMoreWriteupsNote && (
              <p className="projects-note">More project write-ups are being added as I clean up and document my work.</p>
            )}
            <div className="projects-more">
              <a
                href="https://github.com/TshimbiluniRSA?tab=repositories"
                target="_blank"
                rel="noopener noreferrer"
                className="projects-more-link"
              >
                Explore more repositories on GitHub →
              </a>
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default Projects;
