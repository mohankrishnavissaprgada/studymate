import { useState, type KeyboardEvent } from 'react';
import './ChatInput.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Send a message..."
          disabled={disabled}
          rows={1}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="send-button"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M7 11L12 6L17 11M12 18V7"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
