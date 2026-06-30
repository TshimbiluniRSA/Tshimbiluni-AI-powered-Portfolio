import React from 'react';
import './Skills.css';
import { useInView } from '../hooks/useInView';
const skillCategories = [
  { icon:'▣', title:'Frontend Engineering', skills:['React','TypeScript','HTML','CSS','Vite','Responsive UI','Component-based architecture'] },
  { icon:'⚙', title:'Backend Engineering', skills:['Python','FastAPI','Django / DRF','REST APIs','PostgreSQL','SQLAlchemy','API integrations'] },
  { icon:'◇', title:'AI and Automation', skills:['LLM integrations','OpenAI','Gemini','Hugging Face','NLP','Prompt engineering','Document AI workflows','Classification and extraction pipelines'] },
  { icon:'↗', title:'DevOps and Delivery', skills:['Docker','Git','GitHub Actions / CI/CD','Linux','Render','Cloud deployments','Environment configuration'] },
  { icon:'✓', title:'Engineering Practices', skills:['Debugging production issues','Clean service-layer design','Background jobs','Database design','Testing mindset','API-first development'] },
];
const Skills: React.FC = () => { const { ref, isInView } = useInView<HTMLElement>(); return <section id="skills" className="skills" ref={ref}><div className="container"><p className="section-kicker">Capabilities</p><h2 className={`section-title reveal ${isInView ? 'is-visible' : ''}`}>How I Build Software</h2><p className="section-intro">A practical capability map across user interfaces, backend services, data, AI workflows, delivery, and engineering discipline.</p><div className="skills-grid">{skillCategories.map((category,index)=><article key={category.title} className={`skill-category reveal ${isInView ? 'is-visible' : ''}`} style={{ '--reveal-delay': `${index * 0.08}s` } as React.CSSProperties}><div className="category-heading"><span>{category.icon}</span><h3>{category.title}</h3></div><div className="skill-list">{category.skills.map((skill,idx)=><span key={skill} className={idx < 2 ? 'skill-item skill-item-strong':'skill-item'}>{skill}</span>)}</div></article>)}</div></div></section>};
export default Skills;
