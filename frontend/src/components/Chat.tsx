import { useState } from 'react';
import { chatAPI } from '../api/client';
import type { Message } from '../api/client';
import './Chat.css';

interface ChatProps {
  isOpen: boolean;
  onClose: () => void;
}

const Chat = ({ isOpen, onClose }: ChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        message: inputMessage,
        session_id: sessionId,
      });

      setSessionId(response.session_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chat-overlay" onClick={onClose}>
      <div className="chat-container" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header">
          <div className="chat-header-content">
            <h3>AI Assistant</h3>
            <p>Ask me anything about Tshimbiluni's portfolio</p>
          </div>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <div className="welcome-icon">👋</div>
              <h4>Welcome! How can I help you?</h4>
              <p>Feel free to ask me about:</p>
              <ul>
                <li>Skills and experience</li>
                <li>Projects and work</li>
                <li>Technologies used</li>
                <li>Contact information</li>
              </ul>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">{message.content}</div>
            </div>
          ))}
          {loading && (
            <div className="message assistant-message">
              <div className="message-content loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={loading || !inputMessage.trim()}
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
