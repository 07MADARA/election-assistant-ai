import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';

// Mock fetch globally
global.fetch = vi.fn();

// Mock Firebase
vi.mock('./firebase', () => ({
  signInUser: vi.fn().mockResolvedValue({ uid: 'test-user-123' }),
  auth: { currentUser: { uid: 'test-user-123' } },
  db: {}
}));

// Mock Firestore
vi.mock('firebase/firestore', () => ({
  collection: vi.fn(),
  addDoc: vi.fn(),
  serverTimestamp: vi.fn()
}));

describe('CivicGuide App', () => {
  it('renders the chat interface with accessibility elements', async () => {
    render(<App />);
    
    expect(screen.getByText('CivicGuide')).toBeInTheDocument();
    
    // Wait for suspense to load ChatWindow
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Type your message here...')).toBeInTheDocument();
    });
    
    // Check if the chat region is aria-live
    const chatRegion = document.querySelector('[aria-live="polite"]');
    expect(chatRegion).toBeInTheDocument();
    
    // Check if the input and send button exist and have correct labels
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument();
  });

  it('allows typing and submitting a message', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'This is a mock bot response.' })
    });

    render(<App />);
    
    // Wait for suspense
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Type your message here...')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText('Type your message here...');
    const sendBtn = screen.getByRole('button', { name: 'Send message' });

    fireEvent.change(input, { target: { value: 'How do I vote?' } });
    expect(input.value).toBe('How do I vote?');
    expect(sendBtn).not.toBeDisabled();

    fireEvent.click(sendBtn);

    // After click, input should be cleared and loading should appear
    expect(input.value).toBe('');
    expect(screen.getByText('Assistant is typing')).toBeInTheDocument();

    // Wait for the bot response to appear
    await waitFor(() => {
      expect(screen.getByText('This is a mock bot response.')).toBeInTheDocument();
    });
  });
});
