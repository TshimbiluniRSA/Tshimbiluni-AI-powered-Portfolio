import { skills } from '../content/profile';
import './Skills.css';

export default function Skills() {
  return (
    <section id="skills" className="section" aria-labelledby="skills-title">
      <div className="container">
        <header className="section-header">
          <span className="eyebrow">Skills</span>
          <h2 id="skills-title" className="section-title">
            Tools I use in production
          </h2>
        </header>

        <div className="skills-grid">
          {skills.map((group) => (
            <div key={group.area} className="skills-group">
              <h3 className="skills-group__title">{group.area}</h3>
              <ul className="tag-list">
                {group.items.map((item) => (
                  <li key={item} className="tag">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
