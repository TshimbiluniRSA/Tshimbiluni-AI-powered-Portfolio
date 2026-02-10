import React, { useEffect, useState } from 'react';
import './Projects.css';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        // Fetch featured repositories
        const response = await fetch('/api/repositories/featured');
        const data = await response.json();
        setProjects(data);
      } catch (error) {
        console.error('Failed to fetch projects:', error);
        // Fallback: fetch all repos
        try {
          const response = await fetch('/api/repositories/TshimbiluniRSA?size=6');
          const data = await response.json();
          setProjects(data.items || []);
        } catch (fallbackError) {
          console.error('Fallback fetch failed:', fallbackError);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) {
    return (
      <section id="projects" className="projects">
        <div className="container">
          <h2 className="section-title">Featured Projects</h2>
          <p className="loading">Loading projects...</p>
        </div>
      </section>
    );
  }

  return (
    <section id="projects" className="projects">
      <div className="container">
        <h2 className="section-title">Featured Projects</h2>
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <h3 className="project-title">{project.name}</h3>
              <p className="project-description">
                {project.description || 'No description available'}
              </p>
              
              {/* Language badge */}
              {project.language && (
                <span className="language-badge">{project.language}</span>
              )}
              
              {/* Technologies from topics */}
              {project.topics && project.topics.length > 0 && (
                <div className="project-technologies">
                  {project.topics.slice(0, 5).map((topic: string, idx: number) => (
                    <span key={idx} className="tech-tag">{topic}</span>
                  ))}
                </div>
              )}
              
              {/* Stats */}
              <div className="project-stats">
                <span>⭐ {project.stars || 0}</span>
                <span>🔱 {project.forks || 0}</span>
              </div>
              
              <a 
                href={project.html_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="project-link"
              >
                View on GitHub →
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Projects;
