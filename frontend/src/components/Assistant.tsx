import Chat from './Chat';
import './Assistant.css';

export default function Assistant() {
  return (
    <section id="assistant" className="section section--subtle" aria-labelledby="assistant-title">
      <div className="container assistant">
        <header className="assistant__intro">
          <span className="eyebrow">AI assistant</span>
          <h2 id="assistant-title" className="section-title">
            Ask about my experience
          </h2>
          <p className="section-lead">
            An assistant built into this site answers questions about my work, projects and skills.
            It uses the OpenAI API with my profile as its only source, so it stays on topic.
          </p>
          <ul className="assistant__facts">
            <li>Grounded in my CV and project details</li>
            <li>Rate limited and cost capped on the server</li>
            <li>Answers are AI-generated; my CV is the authoritative source</li>
          </ul>
        </header>
        <Chat />
      </div>
    </section>
  );
}
