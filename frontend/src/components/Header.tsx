import React, { useEffect, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import './Header.css';

const navItems = [
  { id: 'hero', label: 'Home' },
  { id: 'about', label: 'About' },
  { id: 'building', label: 'Direction' },
  { id: 'skills', label: 'Skills' },
  { id: 'projects', label: 'Projects' },
  { id: 'contact', label: 'Contact' },
];

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [activeSection, setActiveSection] = useState('hero');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const sections = navItems.map(item => document.getElementById(item.id)).filter(Boolean) as HTMLElement[];
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible?.target.id) setActiveSection(visible.target.id);
    }, { rootMargin: '-30% 0px -55% 0px', threshold: [0.1, 0.3, 0.6] });
    sections.forEach(section => observer.observe(section));
    return () => observer.disconnect();
  }, []);
  
  const scrollToSection = (sectionId: string) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
    setIsMobileMenuOpen(false);
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <button className="brand" onClick={() => scrollToSection('hero')} aria-label="Go to home section">
            <span className="brand-mark">TN</span>
            <span className="brand-name">Tshimbiluni Nedambale</span>
          </button>
          <button className="mobile-menu-toggle" onClick={() => setIsMobileMenuOpen(open => !open)} aria-label="Toggle navigation menu" aria-expanded={isMobileMenuOpen} aria-controls="primary-navigation"><span></span><span></span><span></span></button>
          <nav id="primary-navigation" className={`nav ${isMobileMenuOpen ? 'nav-open' : ''}`} aria-label="Primary navigation">
            {navItems.map(item => <button key={item.id} onClick={() => scrollToSection(item.id)} className={activeSection === item.id ? 'active' : ''}>{item.label}</button>)}
            <button onClick={toggleTheme} className="theme-toggle" aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`} title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>
              <span aria-hidden="true">{theme === 'light' ? '☾' : '☀'}</span><span className="theme-label">Theme</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
export default Header;
