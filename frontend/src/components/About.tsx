import './About.css';

const About = () => {
  return (
    <section id="about" className="about">
      <div className="container">
        <h2 className="section-title">About Me</h2>
        <div className="about-content">
          <div className="about-text">
            <p>
              I'm a passionate Full Stack Developer with a strong focus on building scalable
              web applications and integrating AI technologies. With expertise in modern
              frameworks and cloud technologies, I create solutions that make a difference.
            </p>
            <p>
              My journey in software development has equipped me with a diverse skill set,
              ranging from frontend frameworks like React to backend technologies like Python
              and FastAPI. I'm constantly learning and adapting to new technologies to stay
              at the forefront of the industry.
            </p>
            <p>
              When I'm not coding, I enjoy contributing to open-source projects, sharing
              knowledge with the developer community, and exploring the latest advancements
              in artificial intelligence and machine learning.
            </p>
          </div>
          <div className="about-highlights">
            <div className="highlight-card">
              <div className="highlight-icon">🚀</div>
              <h3>Fast Learner</h3>
              <p>Quick to adapt to new technologies and frameworks</p>
            </div>
            <div className="highlight-card">
              <div className="highlight-icon">💡</div>
              <h3>Problem Solver</h3>
              <p>Creative solutions to complex challenges</p>
            </div>
            <div className="highlight-card">
              <div className="highlight-icon">🤝</div>
              <h3>Team Player</h3>
              <p>Collaborative approach to development</p>
            </div>
            <div className="highlight-card">
              <div className="highlight-icon">🎯</div>
              <h3>Goal Oriented</h3>
              <p>Focused on delivering quality results</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
