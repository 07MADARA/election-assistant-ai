import React, { useState, useEffect, Suspense } from 'react';
import { signInUser } from './firebase';
import { AlertCircle } from 'lucide-react';

const ChatWindow = React.lazy(() => import('./ChatWindow'));

const App: React.FC = () => {
  const [authError, setAuthError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        await signInUser();
        setIsAuthenticated(true);
      } catch (err) {
        console.error("Firebase auth failed, continuing without auth:", err);
        // Continue even if Firebase isn't configured for local dev
        setIsAuthenticated(true); 
      }
    };
    initAuth();
  }, []);

  return (
    <main className="app-container">
      <header className="app-header">
        <h1>CivicGuide</h1>
        <p>Your Neutral Election Process Assistant</p>
      </header>

      {authError && (
        <div className="error-message" style={{ color: 'red', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem' }}>
          <AlertCircle size={16} />
          <span>{authError}</span>
        </div>
      )}

      {isAuthenticated ? (
        <Suspense fallback={<div className="loading-indicator">Loading Chat...</div>}>
          <ChatWindow />
        </Suspense>
      ) : (
        <div className="loading-indicator">Authenticating...</div>
      )}
    </main>
  );
};

export default App;
