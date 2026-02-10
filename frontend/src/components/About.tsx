import React, { useEffect, useState } from 'react';
import './About.css';

interface CVExperience {
  title: string;
  company: string;
  duration: string;
}

interface CVData {
  summary?: string;
  experience?: CVExperience[];
}

const About: React.FC = () => {
  const [cvData, setCvData] = useState<CVData | null>(null);
  
  useEffect(() => {
    fetch('/api/cv/info')
      .then(res => res.json())
      .then(setCvData)
      .catch(console.error);
  }, []);

  return (
    <section id="about" className="about">
      <div className="container">
        <h2 className="section-title">About Me</h2>
        <div className="about-content">
          <div className="about-text">
            {cvData?.summary ? (
              <p>{cvData.summary}</p>
            ) : (
              <p>
                I'm a passionate developer specializing in AI-powered applications and modern web technologies.
                With expertise in both frontend and backend development, I create intelligent solutions
                that leverage the latest advancements in artificial intelligence.
              </p>
            )}
            
            {cvData?.experience && cvData.experience.length > 0 && (
              <div className="experience-highlight">
                <h3>Current Role</h3>
                <p className="role-title">{cvData.experience[0].title}</p>
                <p className="role-company">{cvData.experience[0].company}</p>
                <p className="role-duration">{cvData.experience[0].duration}</p>
              </div>
            )}
          </div>
          
          <div className="about-highlights">
            <div className="highlight-card">
              <h3>💻 Full Stack Development</h3>
              <p>React, TypeScript, Python, FastAPI</p>
            </div>
            <div className="highlight-card">
              <h3>🤖 AI & Machine Learning</h3>
              <p>LLMs, NLP, Gemini, OpenAI Integration</p>
            </div>
            <div className="highlight-card">
              <h3>🚀 DevOps & Cloud</h3>
              <p>Docker, CI/CD, PostgreSQL, Render</p>
            </div>
            
            {/* Add CV Download Button */}
            <button 
              onClick={() => window.open('/api/cv/download', '_blank')}
              className="download-cv-btn"
            >
              📄 Download Resume
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
