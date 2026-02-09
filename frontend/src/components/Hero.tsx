import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { GitHubProfile } from '../api/client';
import './Hero.css';

const Hero: React.FC = () => {
  const [githubProfile, setGithubProfile] = useState<GitHubProfile | null>(null);
  const githubUsername = import.meta.env.VITE_GITHUB_USERNAME || 'TshimbiluniRSA';

  useEffect(() => {
    const fetchGitHubProfile = async () => {
      try {
        // Try to sync first
        await api.github.sync(githubUsername);
        // Then fetch the profile
        const profile = await api.github.getProfile(githubUsername);
        setGithubProfile(profile);
      } catch (error) {
        console.error('Failed to fetch GitHub profile:', error);
      }
    };

    fetchGitHubProfile();
  }, [githubUsername]);

  return (
    <section id="hero" className="hero">
      <div className="container">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Hi, I'm <span className="highlight">Tshimbiluni</span>
            </h1>
            <h2 className="hero-subtitle">
              AI-Powered Portfolio Developer
            </h2>
            <p className="hero-description">
              Building innovative solutions with cutting-edge AI technology.
              Passionate about creating intelligent applications that make a difference.
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
