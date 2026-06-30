import React, { useEffect, useState } from 'react';
import './About.css';
import { api } from '../api/client';
import { useInView } from '../hooks/useInView';
interface CVExperience { title: string; company: string; duration: string; }
interface CVData { experience?: CVExperience[]; }
const highlights = [
  ['💻','Full-stack engineering','I build across the stack — from responsive React interfaces to backend APIs, databases, and deployment workflows.'],
  ['🤖','AI-powered systems','I am focused on practical AI applications such as document processing, extraction, classification, LLM integration, and workflow automation.'],
  ['🛠','Production mindset','I care about reliability, debugging, clean architecture, CI/CD, environment setup, logging, and building software that can survive real usage.'],
  ['📈','Career growth','I am actively growing toward AI engineering and backend-focused system design, with a strong focus on building real products, not just tutorials.'],
];
const About: React.FC = () => {
  const [cvData, setCvData] = useState<CVData | null>(null);
  const { ref, isInView } = useInView<HTMLElement>();
  useEffect(() => { api.cv.getInfo().then(setCvData).catch(console.error); }, []);
  return <section id="about" className="about" ref={ref}><div className="container"><p className="section-kicker">Profile</p><h2 className={`section-title reveal ${isInView ? 'is-visible' : ''}`}>About Me</h2><div className="about-content"><div className={`about-text reveal ${isInView ? 'is-visible' : ''}`}><p>I am a software engineer from South Africa with a strong interest in full-stack development, backend systems, and AI-powered automation. I enjoy building applications that are not only visually clean, but also useful, reliable, and connected to real business processes.</p><p>My experience spans frontend development with React and TypeScript, backend development with Python, Django, FastAPI, and PostgreSQL, and deployment workflows using Docker, CI/CD, and cloud platforms. I have also worked on document-processing and automation systems where AI is used to classify, extract, and move data through business workflows.</p><p>What drives me is the gap between ideas and execution. I like taking a concept, breaking it into technical pieces, building the system, debugging the difficult parts, and improving it until it becomes something people can actually use.</p>{cvData?.experience?.[0] && <div className="experience-highlight"><h3>Current Role</h3><p className="role-title">{cvData.experience[0].title}</p><p>{cvData.experience[0].company} · {cvData.experience[0].duration}</p></div>}<button onClick={() => api.cv.download()} className="download-cv-btn">Download Resume</button></div><div className="about-highlights">{highlights.map(([icon,title,text], index) => <article key={title} className={`highlight-row reveal ${isInView ? 'is-visible' : ''}`} style={{ '--reveal-delay': `${index * 0.08}s` } as React.CSSProperties}><span>{icon}</span><div><h3>{title}</h3><p>{text}</p></div></article>)}</div></div></div></section>;
};
export default About;
