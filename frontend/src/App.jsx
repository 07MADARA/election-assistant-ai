import React, { useState, useRef, useEffect, useCallback } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { Send, AlertCircle } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: 'Hello! I am CivicGuide, your election process assistant. Are you currently registered to vote, or do you need help getting started?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Debounced submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // In production, point to the actual backend URL if separated, 
      // but since they are served together, relative path works.
      const API_URL = import.meta.env.VITE_API_URL || '/api/chat';
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [...messages, userMsg] })
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with the assistant. Please try again.');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'bot', content: data.reply }]);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Safe HTML rendering
  const renderMarkdown = (text) => {
    const rawHtml = marked.parse(text);
    return { __html: DOMPurify.sanitize(rawHtml) };
  };

  return (
    <main className="app-container">
      <header className="app-header">
        <h1>CivicGuide</h1>
        <p>Your Neutral Election Process Assistant</p>
      </header>

      <section 
        className="chat-container" 
        aria-live="polite" 
        aria-atomic="false"
      >
        {messages.map((msg, idx) => (
          <article key={idx} className={`message ${msg.role}`}>
            <div 
              className="message-content" 
              dangerouslySetInnerHTML={renderMarkdown(msg.content)} 
            />
          </article>
        ))}
        {isLoading && (
          <div className="loading-indicator" aria-label="Assistant is typing">
            <span>Assistant is typing</span>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
        {error && (
          <div className="error-message" style={{ color: 'red', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </section>

      <section className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <label htmlFor="chat-input" className="sr-only" style={{display: 'none'}}>Type your message</label>
          <input
            id="chat-input"
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            disabled={isLoading}
            autoComplete="off"
          />
          <button 
            type="submit" 
            className="send-button" 
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        </form>
      </section>
    </main>
  );
}
