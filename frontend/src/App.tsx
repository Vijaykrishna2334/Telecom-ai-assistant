import { useState, useEffect } from 'react';
import './styles/globals.css';
import ChatWindow from './components/Chat/ChatWindow';
import Header from './components/Layout/Header';
import type { Message } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    // Initialize with welcome message
    const welcomeMessage: Message = {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your Telecom AI Assistant. How can I help you today? You can ask me about plans, billing, network issues, or anything else related to your telecom service.',
      timestamp: new Date(),
      messageType: 'text',
    };
    setMessages([welcomeMessage]);
  }, []);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
      messageType: 'text',
    };
    setMessages(prev => [...prev, userMessage]);

    // TODO: Call API to get response
    // For now, add a placeholder response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I received your message. The backend API integration is ready to process your request.',
        timestamp: new Date(),
        messageType: 'text',
      };
      setMessages(prev => [...prev, assistantMessage]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
