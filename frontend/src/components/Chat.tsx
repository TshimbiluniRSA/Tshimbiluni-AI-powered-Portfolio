import { useEffect, useRef, useState } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api, apiErrorMessage, CHAT_MESSAGE_MAX_LENGTH } from '../api/client';
import { suggestedQuestions } from '../content/profile';
import { SendIcon } from './icons';
import './Chat.css';

interface Message {
  key: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
}

const COUNTER_THRESHOLD = CHAT_MESSAGE_MAX_LENGTH - 200;

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const logRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || loading) return;

    setMessages((current) => [
      ...current,
      { key: crypto.randomUUID(), role: 'user', content: message },
    ]);
    setInput('');
    setLoading(true);
    try {
      const reply = await api.chat.sendMessage({ message, session_id: sessionId });
      setMessages((current) => [
        ...current,
        { key: crypto.randomUUID(), role: 'assistant', content: reply.content },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          key: crypto.randomUUID(),
          role: 'error',
          content:
            apiErrorMessage(error) ?? 'The assistant could not answer right now. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    void send(input);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void send(input);
    }
  };

  return (
    <div className="chat">
      <div
        ref={logRef}
        className="chat__log"
        role="log"
        aria-live="polite"
        aria-busy={loading}
        aria-label="Conversation with the portfolio assistant"
      >
        {messages.length === 0 ? (
          <div className="chat__empty">
            <p className="chat__empty-title">Ask anything about my work</p>
            <p>Try one of these, or write your own question.</p>
            <div className="chat__suggestions">
              {suggestedQuestions.map((question) => (
                <button
                  key={question}
                  type="button"
                  className="chat__suggestion"
                  onClick={() => void send(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.key} className={`chat__message chat__message--${message.role}`}>
              {message.role === 'assistant' ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ href, children }) => (
                      <a href={href} target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="chat__message chat__message--assistant chat__typing">
            <span className="visually-hidden">The assistant is typing</span>
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            <span aria-hidden="true" />
          </div>
        )}
      </div>

      <form className="chat__form" onSubmit={onSubmit}>
        <label htmlFor="chat-input" className="visually-hidden">
          Your question
        </label>
        <textarea
          id="chat-input"
          ref={inputRef}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask a question…"
          maxLength={CHAT_MESSAGE_MAX_LENGTH}
          rows={1}
          disabled={loading}
        />
        <button
          type="submit"
          className="btn btn--primary chat__send"
          disabled={loading || !input.trim()}
          aria-label="Send question"
        >
          <SendIcon />
        </button>
        {input.length > COUNTER_THRESHOLD && (
          <p className="chat__counter" aria-live="polite">
            {input.length}/{CHAT_MESSAGE_MAX_LENGTH}
          </p>
        )}
      </form>
    </div>
  );
}
