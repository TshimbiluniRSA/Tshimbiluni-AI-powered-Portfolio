import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { GitHubProfile } from '../api/client';
import './Hero.css';

const Hero: React.FC = () => {
  const [githubProfile, setGithubProfile] = useState<GitHubProfile | null>(null);
  const [cvData, setCvData] = useState<any>(null);
  const githubUsername = import.meta.env.VITE_GITHUB_USERNAME || 'TshimbiluniRSA';

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch GitHub profile
        await api.github.sync(githubUsername);
        const profile = await api.github.getProfile(githubUsername);
        setGithubProfile(profile);
        
        // Fetch CV data
        const cv = await fetch('/api/cv/info').then(res => res.json());
        setCvData(cv);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    fetchData();
  }, [githubUsername]);

  return (
    <section id="hero" className="hero">
      <div className="container">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Hi, I'm <span className="highlight">{githubProfile?.name || 'Tshimbiluni Nedambale'}</span>
            </h1>
            <h2 className="hero-subtitle">
              {cvData?.summary?.split('.')[0] || 'Full Stack Developer & AI Engineer'}
            </h2>
            <p className="hero-description">
              {cvData?.summary || githubProfile?.bio || 
               'Passionate about building intelligent applications that solve real-world problems.'}
            </p>
            <div className="hero-actions">
              <a href="#projects" className="btn btn-primary">View Projects</a>
              <a href="#about" className="btn btn-secondary">Learn More</a>
            </div>
          </div>
          
          {githubProfile && (
            <div className="hero-profile">
              {githubProfile.avatar_url && (
                <img 
                  src={githubProfile.avatar_url} 
                  alt={githubProfile.name || githubProfile.username}
                  className="profile-image"
                />
              )}
              <div className="profile-stats">
                <div className="stat">
                  <span className="stat-value">{githubProfile.public_repos || 0}</span>
                  <span className="stat-label">Repositories</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{githubProfile.followers || 0}</span>
                  <span className="stat-label">Followers</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{githubProfile.following || 0}</span>
                  <span className="stat-label">Following</span>
                </div>
              </div>
              {githubProfile.profile_url && (
                <a 
                  href={githubProfile.profile_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="github-link"
                >
                  View GitHub Profile →
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Hero;
