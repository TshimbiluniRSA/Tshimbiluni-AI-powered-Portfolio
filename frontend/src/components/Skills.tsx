import React from 'react';
import './Skills.css';

const Skills: React.FC = () => {
  const skillCategories = [
    {
      title: 'Frontend',
      skills: ['React', 'TypeScript', 'HTML/CSS', 'Vite', 'Responsive Design']
    },
    {
      title: 'Backend',
      skills: ['Python', 'FastAPI', 'Node.js', 'REST APIs', 'SQLAlchemy']
    },
    {
      title: 'AI & ML',
      skills: ['LLaMA', 'OpenAI', 'Hugging Face', 'NLP', 'Prompt Engineering']
    },
    {
      title: 'DevOps & Tools',
      skills: ['Docker', 'Git', 'CI/CD', 'Linux', 'PostgreSQL']
    }
  ];

  return (
    <section id="skills" className="skills">
      <div className="container">
        <h2 className="section-title">Skills & Technologies</h2>
        <div className="skills-grid">
          {skillCategories.map((category, index) => (
            <div key={index} className="skill-category">
              <h3 className="category-title">{category.title}</h3>
              <ul className="skill-list">
                {category.skills.map((skill, skillIndex) => (
                  <li key={skillIndex} className="skill-item">{skill}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Skills;
