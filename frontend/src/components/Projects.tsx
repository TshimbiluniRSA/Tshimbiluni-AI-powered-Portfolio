import React from 'react';
import './Projects.css';

const Projects: React.FC = () => {
  const projects = [
    {
      title: 'AI-Powered Portfolio',
      description: 'A modern portfolio with integrated AI chat assistant, GitHub/LinkedIn sync, and responsive design.',
      technologies: ['React', 'TypeScript', 'FastAPI', 'LLaMA', 'Docker'],
      github: 'https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio',
    },
    {
      title: 'GitHub Profile Sync',
      description: 'Automated system for fetching and displaying GitHub profile data with real-time updates.',
      technologies: ['Python', 'FastAPI', 'SQLAlchemy', 'GitHub API'],
    },
    {
      title: 'Chat with AI',
      description: 'Conversational AI interface supporting multiple LLM providers including OpenAI and LLaMA.',
      technologies: ['React', 'Python', 'OpenAI', 'Streaming APIs'],
    },
  ];

  return (
    <section id="projects" className="projects">
      <div className="container">
        <h2 className="section-title">Featured Projects</h2>
        <div className="projects-grid">
          {projects.map((project, index) => (
            <div key={index} className="project-card">
              <h3 className="project-title">{project.title}</h3>
              <p className="project-description">{project.description}</p>
              <div className="project-technologies">
                {project.technologies.map((tech, techIndex) => (
                  <span key={techIndex} className="tech-tag">{tech}</span>
                ))}
              </div>
              {project.github && (
                <a 
                  href={project.github} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="project-link"
                >
                  View on GitHub →
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Projects;
