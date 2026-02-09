import './Skills.css';

const Skills = () => {
  const skillCategories = [
    {
      title: 'Frontend',
      icon: '🎨',
      skills: ['React', 'TypeScript', 'JavaScript', 'HTML5', 'CSS3', 'Vite', 'Responsive Design']
    },
    {
      title: 'Backend',
      icon: '⚙️',
      skills: ['Python', 'FastAPI', 'Node.js', 'REST APIs', 'WebSockets', 'Authentication']
    },
    {
      title: 'AI & ML',
      icon: '🤖',
      skills: ['OpenAI API', 'LangChain', 'RAG Systems', 'Prompt Engineering', 'AI Integration']
    },
    {
      title: 'Database',
      icon: '💾',
      skills: ['PostgreSQL', 'MongoDB', 'Redis', 'SQL', 'Database Design']
    },
    {
      title: 'DevOps',
      icon: '🚀',
      skills: ['Docker', 'CI/CD', 'Git', 'GitHub Actions', 'Cloud Deployment', 'Nginx']
    },
    {
      title: 'Tools',
      icon: '🛠️',
      skills: ['VS Code', 'Postman', 'Linux', 'Agile', 'Version Control']
    }
  ];

  return (
    <section id="skills" className="skills">
      <div className="container">
        <h2 className="section-title">Skills & Technologies</h2>
        <div className="skills-grid">
          {skillCategories.map((category, index) => (
            <div key={index} className="skill-category">
              <div className="category-header">
                <span className="category-icon">{category.icon}</span>
                <h3 className="category-title">{category.title}</h3>
              </div>
              <div className="skills-list">
                {category.skills.map((skill, skillIndex) => (
                  <span key={skillIndex} className="skill-tag">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Skills;
