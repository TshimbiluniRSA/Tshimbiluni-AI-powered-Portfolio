import React, { useEffect, useState } from 'react';
import './Skills.css';

const Skills: React.FC = () => {
  const [skills, setSkills] = useState<string[]>([]);
  
  useEffect(() => {
    fetch('/api/cv/info')
      .then(res => res.json())
      .then(data => {
        if (data.skills) {
          setSkills(data.skills);
        }
      })
      .catch(console.error);
  }, []);

  // Categorize skills (simple heuristic)
  const categorizeSkills = (allSkills: string[]) => {
    const categories: { [key: string]: string[] } = {
      'Frontend': ['React', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Vite', 'Tailwind', 'Vue', 'Angular'],
      'Backend': ['Python', 'FastAPI', 'Node.js', 'Django', 'Flask', 'REST', 'GraphQL', 'Express'],
      'AI & ML': ['OpenAI', 'LLaMA', 'Gemini', 'Machine Learning', 'NLP', 'TensorFlow', 'PyTorch', 'Hugging Face'],
      'DevOps': ['Docker', 'Kubernetes', 'CI/CD', 'Git', 'Linux', 'AWS', 'PostgreSQL', 'MongoDB', 'Redis'],
    };
    
    const result: { [key: string]: string[] } = {};
    Object.keys(categories).forEach(cat => {
      result[cat] = allSkills.filter(skill => 
        categories[cat].some(tech => 
          skill.toLowerCase().includes(tech.toLowerCase())
        )
      );
    });
    
    // Add uncategorized skills to "Other"
    const categorized = Object.values(result).flat();
    result['Other'] = allSkills.filter(s => !categorized.includes(s));
    
    return result;
  };

  const skillCategories: { [key: string]: string[] } = skills.length > 0 ? categorizeSkills(skills) : {
    'Frontend': ['React', 'TypeScript', 'HTML/CSS', 'Vite', 'Responsive Design'],
    'Backend': ['Python', 'FastAPI', 'Node.js', 'REST APIs', 'SQLAlchemy'],
    'AI & ML': ['LLaMA', 'OpenAI', 'Hugging Face', 'NLP', 'Prompt Engineering'],
    'DevOps & Tools': ['Docker', 'Git', 'CI/CD', 'Linux', 'PostgreSQL']
  };

  return (
    <section id="skills" className="skills">
      <div className="container">
        <h2 className="section-title">Skills & Technologies</h2>
        <div className="skills-grid">
          {Object.entries(skillCategories).map(([category, categorySkills]) => (
            categorySkills.length > 0 && (
              <div key={category} className="skill-category">
                <h3 className="category-title">{category}</h3>
                <ul className="skill-list">
                  {categorySkills.map((skill, idx) => (
                    <li key={idx} className="skill-item">{skill}</li>
                  ))}
                </ul>
              </div>
            )
          ))}
        </div>
      </div>
    </section>
  );
};

export default Skills;
