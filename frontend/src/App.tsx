import { useState, useEffect, useRef } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import type { Message } from './types';
import { sendMessage, checkHealth } from './api/chat';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkHealth().then(setIsConnected);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(content);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Assistant</h1>
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <h2>How can I help you today?</h2>
            <p>Ask me anything about the documents in the knowledge base</p>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}

export default App;
