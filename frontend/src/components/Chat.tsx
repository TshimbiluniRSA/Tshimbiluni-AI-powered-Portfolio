import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../api/client';
import type { ChatMessage } from '../api/client';
import './Chat.css';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const messagesRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      session_id: sessionId,
      message_type: 'user',
      content: inputValue,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await api.chat.sendMessage({
        message: inputValue,
        session_id: sessionId,
      });

      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        session_id: sessionId,
        message_type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h3>AI Assistant</h3>
      </div>

      <div
        ref={messagesRef}
        className="chat-messages"
        role="log"
        aria-live="polite"
        aria-relevant="additions"
        aria-busy={isLoading}
        aria-label="Conversation history"
      >
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>
              👋 Hi! I'm Tshimbi's portfolio assistant. Ask me about his skills,
              experience, projects, or career direction. For best results, keep
              questions short and specific.
            </p>
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.message_type === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-content">
              {message.message_type === 'user' ? (
                message.content
              ) : (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Open all assistant-provided links in a new tab.
                    a: ({ href, children }: React.ComponentProps<'a'>) => (
                      <a href={href} target="_blank" rel="noopener noreferrer">
                        {children}
                      </a>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              )}
            </div>
            {message.message_type === 'assistant' && message.response_time_ms && (
              <div className="message-meta">
                Responded in {message.response_time_ms}ms
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant-message">
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message..."
          aria-label="Message the AI portfolio assistant"
          disabled={isLoading}
          rows={1}
        />
        <button 
          onClick={handleSendMessage} 
          disabled={!inputValue.trim() || isLoading}
          className="send-btn"
          aria-label="Send message"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
