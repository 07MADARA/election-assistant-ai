import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import { Send, AlertCircle } from 'lucide-react';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db, auth } from './firebase';

interface ChatMessage {
  role: 'user' | 'model';
  content: string;
}

/**
 * Memoized single message component to prevent re-renders of the entire chat history.
 */
const MessageItem = React.memo(({ msg }: { msg: ChatMessage }) => {
  // Safe HTML rendering memoized
  const renderedContent = useMemo(() => {
    const rawHtml = marked.parse(msg.content);
    return { __html: DOMPurify.sanitize(rawHtml as string) };
  }, [msg.content]);

  return (
    <article className={`message ${msg.role}`}>
      <div 
        className="message-content" 
        dangerouslySetInnerHTML={renderedContent} 
      />
    </article>
  );
});

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'model',
      content: 'Hello! I am CivicGuide, your election process assistant. Are you currently registered to vote, or do you need help getting started?'
    }
  ]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  /**
   * Save message to Firestore
   */
  const saveToFirestore = useCallback(async (msgs: ChatMessage[]) => {
    if (!auth.currentUser) return;
    try {
      await addDoc(collection(db, 'chat_sessions'), {
        userId: auth.currentUser.uid,
        messages: msgs,
        timestamp: serverTimestamp()
      });
    } catch (err) {
      console.error("Failed to save to Firestore:", err);
    }
  }, []);

  /**
   * Handle user submission
   */
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content: input.trim() };
    const newMessages = [...messages, userMsg];
    
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const API_URL = import.meta.env.VITE_API_URL || '/api/chat';
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      });

      if (!response.ok) {
        throw new Error('Failed to communicate with the assistant. Please try again.');
      }

      const data = await response.json();
      const botMsg: ChatMessage = { role: 'model', content: data.reply };
      const finalMessages = [...newMessages, botMsg];
      
      setMessages(finalMessages);
      
      // Save history to Firebase asynchronously
      saveToFirestore(finalMessages);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, messages, saveToFirestore]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  }, []);

  return (
    <>
      <section 
        className="chat-container" 
        aria-live="polite" 
        aria-atomic="false"
      >
        {messages.map((msg, idx) => (
          <MessageItem key={idx} msg={msg} />
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
            onChange={handleInputChange}
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
    </>
  );
};

export default ChatWindow;
