import React from 'react';
import './About.css';

const About: React.FC = () => {
  return (
    <section id="about" className="about">
      <div className="container">
        <h2 className="section-title">About Me</h2>
        <div className="about-content">
          <div className="about-text">
            <p>
              I'm a passionate developer specializing in AI-powered applications and modern web technologies.
              With expertise in both frontend and backend development, I create intelligent solutions
              that leverage the latest advancements in artificial intelligence.
            </p>
            <p>
              My work focuses on building scalable, user-friendly applications that integrate
              machine learning and natural language processing to solve real-world problems.
              I'm constantly exploring new technologies and best practices to deliver
              exceptional results.
            </p>
            <p>
              When I'm not coding, I enjoy contributing to open-source projects, learning about
              emerging technologies, and sharing knowledge with the developer community.
            </p>
          </div>
          <div className="about-highlights">
            <div className="highlight-card">
              <h3>💻 Full Stack Development</h3>
              <p>Building end-to-end solutions with modern frameworks</p>
            </div>
            <div className="highlight-card">
              <h3>🤖 AI Integration</h3>
              <p>Implementing LLMs and ML models in production</p>
            </div>
            <div className="highlight-card">
              <h3>🚀 Cloud & DevOps</h3>
              <p>Deploying scalable applications with Docker & CI/CD</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
