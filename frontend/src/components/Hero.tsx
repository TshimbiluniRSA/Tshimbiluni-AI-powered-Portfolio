import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { GitHubProfile } from '../api/client';
import './Hero.css';

const roles = ['Full Stack Development','Backend Engineering','AI Engineering','Automation Systems','Python Development','React + TypeScript','Production-minded Engineering'];
const badges = ['Python','React','TypeScript','FastAPI','Django','PostgreSQL','AI Workflows','Docker'];

const Hero: React.FC = () => {
  const [githubProfile, setGithubProfile] = useState<GitHubProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [roleIndex, setRoleIndex] = useState(0);
  const githubUsername = import.meta.env.VITE_GITHUB_USERNAME || 'TshimbiluniRSA';

  useEffect(() => {
    const timer = window.setInterval(() => setRoleIndex(index => (index + 1) % roles.length), 2200);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        await api.github.sync(githubUsername);
        const [profile] = await Promise.all([api.github.getProfile(githubUsername), api.cv.getInfo()]);
        setGithubProfile(profile);
      } catch (error) { console.error('Failed to fetch data:', error); }
      finally { setIsLoading(false); }
    };
    fetchData();
  }, [githubUsername]);

  return (
    <section id="hero" className="hero">
      <div className="container">
        <div className="hero-content">
          <div className="hero-text">
            {isLoading ? <HeroSkeleton /> : <>
              <p className="hero-kicker">South African Software Engineer</p>
              <h1 className="hero-title">Hi, I'm <span className="highlight">Tshimbiluni Nedambale.</span></h1>
              <h2 className="hero-subtitle">Software Engineer building AI-powered, full-stack systems.</h2>
              <p className="hero-description">I build practical software that connects clean user interfaces, reliable backend services, databases, automation workflows, and AI integrations. My focus is on turning real business problems into working, production-ready applications.</p>
              <div className="role-rotator" aria-live="polite"><span>I work across:</span><strong>{roles[roleIndex]}</strong></div>
              <div className="hero-badges">{badges.map(badge => <span key={badge}>{badge}</span>)}</div>
              <div className="hero-actions"><a href="#projects" className="btn btn-primary">View My Work →</a><a href="#about" className="btn btn-secondary">Learn About Me</a><button onClick={() => api.cv.download()} className="btn btn-tertiary">Download Resume</button></div>
              {githubProfile?.profile_url && <p className="github-secondary">GitHub: <a href={githubProfile.profile_url} target="_blank" rel="noopener noreferrer">{githubProfile.public_repos || 0} public repos</a></p>}
            </>}
          </div>
          <div className="hero-profile" aria-label="Profile summary">
            {isLoading ? <div className="profile-image skeleton"></div> : githubProfile?.avatar_url && <img src={githubProfile.avatar_url} alt={githubProfile.name || githubProfile.username} className="profile-image" />}
            <div className="profile-card-copy"><span>Backend • AI • Automation</span><p>Building systems that connect frontend UX, APIs, data, AI workflows, and deployment.</p></div>
          </div>
        </div>
      </div>
    </section>
  );
};
const HeroSkeleton = () => <div className="hero-skeleton" aria-label="Loading hero content"><div className="skeleton line short"></div><div className="skeleton line title"></div><div className="skeleton line subtitle"></div><div className="skeleton block"></div><div className="skeleton line buttons"></div></div>;
export default Hero;
