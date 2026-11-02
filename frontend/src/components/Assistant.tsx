import { useRef, useState } from 'react';
import { suggestedQuestions } from '../content/profile';
import { useResumeDownload } from '../hooks/useResumeDownload';
import Chat from './Chat';
import type { ChatHandle } from './Chat';
import './Assistant.css';

const topics = [
  { label: 'At Fluid', question: suggestedQuestions[0] },
  { label: 'AI projects', question: suggestedQuestions[1] },
  { label: 'This site', question: suggestedQuestions[2] },
];

export default function Assistant() {
  const chat = useRef<ChatHandle>(null);
  const [active, setActive] = useState(0);
  const { download, downloading, error } = useResumeDownload();

  return (
    <section id="assistant" className="assistant" aria-labelledby="assistant-title">
      <div className="assistant__plate" data-reveal>
        <Chat ref={chat} />
      </div>

      <div className="assistant__text">
        <div data-reveal>
          <h2 id="assistant-title" className="section-title">
            Ask my assistant
          </h2>
          <p className="assistant__description">
            It answers questions about my work from my CV and project notes, through the OpenAI API
            and this site’s own backend. Answers are generated, so the CV stays the source of truth.
          </p>
        </div>

        <div className="assistant__topics" data-reveal>
          <div className="assistant__tabs" role="group" aria-label="Suggested topics">
            {topics.map((topic, index) => (
              <button
                key={topic.label}
                type="button"
                aria-pressed={active === index}
                onClick={() => setActive(index)}
              >
                {topic.label}
              </button>
            ))}
          </div>
          <p className="assistant__question" aria-live="polite">
            “{topics[active].question}”
          </p>
        </div>

        <div className="assistant__cells" data-reveal>
          <button
            type="button"
            className="assistant__cell assistant__cell--ink"
            onClick={() => chat.current?.ask(topics[active].question)}
          >
            Ask this question
          </button>
          <button
            type="button"
            className="assistant__cell"
            onClick={download}
            disabled={downloading}
            aria-busy={downloading}
          >
            {downloading ? 'Preparing CV…' : 'Download CV'}
          </button>
        </div>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </div>
    </section>
  );
}
