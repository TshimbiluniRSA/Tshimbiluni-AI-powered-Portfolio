import { useState, useEffect } from 'react';
import { githubAPI } from '../api/client';
import type { GitHubProfile } from '../api/client';
import './Hero.css';

const Hero = () => {
  const [profile, setProfile] = useState<GitHubProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const githubUsername = import.meta.env.VITE_GITHUB_USERNAME || 'TshimbiluniRSA';

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await githubAPI.getProfile(githubUsername);
        setProfile(data);
      } catch (error) {
        console.error('Failed to fetch GitHub profile:', error);
        try {
          const syncedData = await githubAPI.syncProfile(githubUsername);
          setProfile(syncedData);
        } catch (syncError) {
          console.error('Failed to sync GitHub profile:', syncError);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [githubUsername]);

  return (
    <section id="hero" className="hero">
      <div className="hero-content">
        <div className="hero-text">
          <h1 className="hero-title">
            Hi, I'm <span className="gradient-text">{profile?.name || 'Tshimbiluni'}</span>
          </h1>
          <p className="hero-subtitle">Full Stack Developer & AI Enthusiast</p>
          <p className="hero-description">
            {profile?.bio || 'Building innovative solutions with modern technologies and AI'}
          </p>
          {!loading && profile && (
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-value">{profile.public_repos}</span>
                <span className="stat-label">Repositories</span>
              </div>
              <div className="stat">
                <span className="stat-value">{profile.followers}</span>
                <span className="stat-label">Followers</span>
              </div>
              <div className="stat">
                <span className="stat-value">{profile.following}</span>
                <span className="stat-label">Following</span>
              </div>
            </div>
          )}
          <div className="hero-buttons">
            {profile?.html_url && (
              <a href={profile.html_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                View GitHub
              </a>
            )}
            <button type="button" onClick={() => document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })} className="btn btn-secondary">
              View Projects
            </button>
          </div>
        </div>
        {profile && (
          <div className="hero-image">
            <img src={profile.avatar_url} alt={profile.name} className="profile-img" />
          </div>
        )}
      </div>
    </section>
  );
};

export default Hero;
