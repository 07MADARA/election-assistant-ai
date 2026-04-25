import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';

// Mock fetch globally
global.fetch = vi.fn();

describe('CivicGuide App', () => {
  it('renders the chat interface with accessibility elements', () => {
    render(<App />);
    
    expect(screen.getByText('CivicGuide')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    
    // Check if the chat region is aria-live
    const chatRegion = document.querySelector('[aria-live="polite"]');
    expect(chatRegion).toBeInTheDocument();
    
    // Check if the input and send button exist and have correct labels
    expect(screen.getByPlaceholderText('Type your message here...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument();
  });

  it('allows typing and submitting a message', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ reply: 'This is a mock bot response.' })
    });

    render(<App />);
    
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
