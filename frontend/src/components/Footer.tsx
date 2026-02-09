import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const githubUsername = import.meta.env.VITE_GITHUB_USERNAME || 'TshimbiluniRSA';
  const twitterUsername = import.meta.env.VITE_TWITTER_USERNAME;
  const linkedinUrl = import.meta.env.VITE_LINKEDIN_URL;

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Tshimbiluni</h3>
            <p>AI-Powered Portfolio Developer</p>
          </div>
          
          <div className="footer-section">
            <h4>Quick Links</h4>
            <nav className="footer-links">
              <a href="#hero">Home</a>
              <a href="#about">About</a>
              <a href="#skills">Skills</a>
              <a href="#projects">Projects</a>
            </nav>
          </div>
          
          <div className="footer-section">
            <h4>Connect</h4>
            <div className="social-links">
              {githubUsername && (
                <a 
                  href={`https://github.com/${githubUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="GitHub"
                >
                  GitHub
                </a>
              )}
              {linkedinUrl && (
                <a 
                  href={linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="LinkedIn"
                >
                  LinkedIn
                </a>
              )}
              {twitterUsername && (
                <a 
                  href={`https://twitter.com/${twitterUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Twitter"
                >
                  Twitter
                </a>
              )}
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {currentYear} Tshimbiluni. All rights reserved.</p>
          <p>Built with React, TypeScript, FastAPI, and AI</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
