import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { GitHubStats } from '../api/client';
import './Hero.css';
const roles=['Full Stack Development','Backend Engineering','AI Engineering','Automation Systems'];
const Hero:React.FC=()=>{
 const [stats,setStats]=useState<GitHubStats|null>(null),[loading,setLoading]=useState(true),[downloadLoading,setDownloadLoading]=useState(false),[error,setError]=useState(''),[role,setRole]=useState(0);
 useEffect(()=>{const id=setInterval(()=>setRole(x=>(x+1)%roles.length),2200);return()=>clearInterval(id)},[]);
 useEffect(()=>{api.github.getStats().then(setStats).catch(()=>setError('GitHub statistics are temporarily unavailable.')).finally(()=>setLoading(false))},[]);
 const download=async()=>{setDownloadLoading(true);setError('');try{const result=await api.cv.download();window.location.assign(result.download_url)}catch{setError('The CV download could not be prepared. Please try again.')}finally{setDownloadLoading(false)}};
 return <section id="hero" className="hero"><div className="container"><div className="hero-content"><div className="hero-text">
 <p className="hero-kicker">South African Software Engineer</p><h1 className="hero-title">Hi, I'm <span className="highlight">Tshimbiluni Nedambale.</span></h1><h2 className="hero-subtitle">Software Engineer building AI-powered, full-stack systems.</h2><p className="hero-description">I build practical software that connects clean interfaces, reliable backend services, databases, automation workflows, and AI integrations.</p>
 <div className="role-rotator" aria-live="polite"><span>I work across:</span><strong>{roles[role]}</strong></div><div className="hero-actions"><a href="#projects" className="btn btn-primary">View My Work →</a><button className="btn btn-tertiary" onClick={download} disabled={downloadLoading} aria-busy={downloadLoading}>{downloadLoading?'Preparing download…':'Download Resume'}</button></div>
 {error&&<p role="status">{error}</p>}{loading?<p>Loading GitHub statistics…</p>:stats?<div className="github-secondary" aria-label="GitHub statistics"><strong>{stats.profile.public_repositories}</strong> repositories · <strong>{stats.repository_stats.total_stars}</strong> stars · <strong>{stats.repository_stats.total_forks}</strong> forks · <strong>{stats.profile.followers}</strong> followers · <strong>{stats.contributions.total}</strong> contributions<br/>Top languages: {stats.top_languages.map(x=>`${x.name} ${x.percentage}%`).join(' · ')||'Not available'}</div>:null}
 </div><div className="hero-profile">{stats?.profile.avatar_url&&<img src={stats.profile.avatar_url} alt={stats.profile.name||stats.username} className="profile-image"/>}<div className="profile-card-copy"><span>Backend • AI • Automation</span><p>Building systems that connect frontend UX, APIs, data, AI workflows, and deployment.</p></div></div></div></div></section>
};export default Hero;
