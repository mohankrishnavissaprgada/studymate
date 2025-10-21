import type { Message } from '../types';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        <div className="message-icon">
          {message.role === 'user' ? '👤' : '🤖'}
        </div>
        <div className="message-text">
          {message.content}
        </div>
      </div>
    </div>
  );
}
