import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">Tshimbiluni</h3>
            <p className="footer-description">
              Full Stack Developer passionate about creating innovative solutions
              with modern technologies and AI.
            </p>
          </div>

          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul className="footer-links">
              <li><a href="#hero" onClick={(e) => { e.preventDefault(); document.getElementById('hero')?.scrollIntoView({ behavior: 'smooth' }); }}>Home</a></li>
              <li><a href="#about" onClick={(e) => { e.preventDefault(); document.getElementById('about')?.scrollIntoView({ behavior: 'smooth' }); }}>About</a></li>
              <li><a href="#skills" onClick={(e) => { e.preventDefault(); document.getElementById('skills')?.scrollIntoView({ behavior: 'smooth' }); }}>Skills</a></li>
              <li><a href="#projects" onClick={(e) => { e.preventDefault(); document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' }); }}>Projects</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Connect</h4>
            <div className="social-links">
              <a href="https://github.com/TshimbiluniRSA" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">💻</span>
                <span>GitHub</span>
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">💼</span>
                <span>LinkedIn</span>
              </a>
              <a href="mailto:contact@tshimbiluni.dev" className="social-link">
                <span className="social-icon">✉️</span>
                <span>Email</span>
              </a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; {currentYear} Tshimbiluni. All rights reserved.</p>
          <p>Built with React, TypeScript & FastAPI</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
