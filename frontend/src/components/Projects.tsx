import './Projects.css';

const Projects = () => {
  const projects = [
    {
      title: 'AI-Powered Portfolio',
      description: 'A modern portfolio website with integrated AI chatbot for interactive user experience. Features real-time chat, GitHub integration, and responsive design.',
      technologies: ['React', 'TypeScript', 'FastAPI', 'OpenAI', 'Docker'],
      github: 'https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio',
      demo: '#',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      title: 'RAG Chat System',
      description: 'Advanced conversational AI system using Retrieval-Augmented Generation. Implements vector databases and context-aware responses.',
      technologies: ['Python', 'LangChain', 'OpenAI', 'PostgreSQL', 'FastAPI'],
      github: '#',
      demo: '#',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    },
    {
      title: 'Full Stack Dashboard',
      description: 'Comprehensive admin dashboard with analytics, user management, and real-time data visualization.',
      technologies: ['React', 'Node.js', 'MongoDB', 'Chart.js', 'WebSockets'],
      github: '#',
      demo: '#',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      title: 'E-Commerce Platform',
      description: 'Scalable e-commerce solution with payment integration, inventory management, and admin panel.',
      technologies: ['React', 'TypeScript', 'Python', 'PostgreSQL', 'Stripe'],
      github: '#',
      demo: '#',
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
    },
    {
      title: 'Social Media API',
      description: 'RESTful API for social media application with authentication, posts, comments, and real-time notifications.',
      technologies: ['FastAPI', 'PostgreSQL', 'Redis', 'JWT', 'WebSockets'],
      github: '#',
      demo: '#',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    },
    {
      title: 'DevOps Pipeline',
      description: 'Automated CI/CD pipeline with Docker containerization, testing, and deployment to cloud infrastructure.',
      technologies: ['Docker', 'GitHub Actions', 'Nginx', 'Linux', 'AWS'],
      github: '#',
      demo: '#',
      gradient: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)'
    }
  ];

  return (
    <section id="projects" className="projects">
      <div className="container">
        <h2 className="section-title">Featured Projects</h2>
        <div className="projects-grid">
          {projects.map((project, index) => (
            <div key={index} className="project-card">
              <div className="project-header" style={{ background: project.gradient }}>
                <h3 className="project-title">{project.title}</h3>
              </div>
              <div className="project-body">
                <p className="project-description">{project.description}</p>
                <div className="project-technologies">
                  {project.technologies.map((tech, techIndex) => (
                    <span key={techIndex} className="tech-badge">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
              <div className="project-footer">
                {project.github !== '#' && (
                  <a href={project.github} target="_blank" rel="noopener noreferrer" className="project-link">
                    <span>GitHub</span>
                    <span>→</span>
                  </a>
                )}
                {project.demo !== '#' && (
                  <a href={project.demo} target="_blank" rel="noopener noreferrer" className="project-link">
                    <span>Live Demo</span>
                    <span>→</span>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Projects;
