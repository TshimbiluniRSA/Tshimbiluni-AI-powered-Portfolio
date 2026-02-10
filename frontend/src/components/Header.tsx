import React from 'react';
import { useTheme } from '../contexts/ThemeContext';
import './Header.css';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <div className="logo">
            <h1>Tshimbiluni Nedambale</h1>
          </div>
          <nav className="nav">
            <button onClick={() => scrollToSection('hero')}>Home</button>
            <button onClick={() => scrollToSection('about')}>About</button>
            <button onClick={() => scrollToSection('skills')}>Skills</button>
            <button onClick={() => scrollToSection('projects')}>Projects</button>
            
            {/* Dark Mode Toggle */}
            <button 
              onClick={toggleTheme} 
              className="theme-toggle"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
