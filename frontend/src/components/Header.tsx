import { useEffect, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import './Header.css';

const navItems = [
  { id: 'work', label: 'Work' },
  { id: 'experience', label: 'Experience' },
  { id: 'assistant', label: 'Assistant' },
  { id: 'contact', label: 'Contact' },
];

/** Plain text navigation laid over the hero photograph. */
export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (event: KeyboardEvent) => event.key === 'Escape' && setMenuOpen(false);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [menuOpen]);

  const nextTheme = theme === 'light' ? 'dark' : 'light';

  return (
    <header className="site-header">
      <button
        type="button"
        className="site-header__menu"
        onClick={() => setMenuOpen((open) => !open)}
        aria-expanded={menuOpen}
        aria-controls="site-nav"
      >
        {menuOpen ? 'Close' : 'Menu'}
      </button>
      <nav
        id="site-nav"
        className={`site-nav${menuOpen ? ' site-nav--open' : ''}`}
        aria-label="Primary"
      >
        <ul>
          {navItems.map((item) => (
            <li key={item.id}>
              <a href={`#${item.id}`} onClick={() => setMenuOpen(false)}>
                {item.label}
              </a>
            </li>
          ))}
          <li>
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={`Switch to ${nextTheme} theme`}
              className="site-nav__theme"
            >
              {theme === 'light' ? 'Dark' : 'Light'}
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
}
