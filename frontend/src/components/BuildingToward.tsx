import React from 'react';
import './BuildingToward.css';
import { useInView } from '../hooks/useInView';

const goals = [
  'Backend systems that are reliable and maintainable',
  'AI workflows that solve practical business problems',
  'Full-stack applications that feel clean and useful',
  'Automation that reduces manual work',
  'Production-ready deployments with proper engineering discipline',
];

const BuildingToward: React.FC = () => {
  const { ref, isInView } = useInView<HTMLElement>();
  return (
    <section id="building" className="building-toward" ref={ref}>
      <div className="container building-band">
        <div className={`building-copy reveal ${isInView ? 'is-visible' : ''}`}>
          <p className="section-kicker">Direction</p>
          <h2>What I’m Building Toward</h2>
          <p>I am building toward becoming an AI-focused software engineer who can design and deliver complete systems — from backend architecture and APIs to AI workflows, automation, deployment, and user experience. My goal is to work on products where AI is not just a feature, but part of a reliable business process.</p>
        </div>
        <ul className="building-map">
          {goals.map((goal, index) => (
            <li key={goal} className={`reveal ${isInView ? 'is-visible' : ''}`} style={{ '--reveal-delay': `${index * 0.08}s` } as React.CSSProperties}>
              <span>{index + 1}</span>{goal}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};
export default BuildingToward;
