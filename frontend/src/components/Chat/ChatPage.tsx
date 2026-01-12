import { useState, useEffect } from 'react';
import ChatWindow from '../Chat/ChatWindow';
import Header from '../Layout/Header';
import type { Message } from '../../types';

function ChatPage() {
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

        // Call backend API to get response
        try {
            const response = await fetch('http://localhost:8080/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: content,
                    session_id: sessionId || undefined,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to get response');
            }

            const data = await response.json();

            if (data.session_id) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.message || 'Sorry, I could not process your request.',
                timestamp: new Date(),
                messageType: 'text',
                ragContext: data.rag_context || undefined,  // Debug: RAG context
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Chat error:', error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, there was an error connecting to the server. Please make sure the backend is running.',
                timestamp: new Date(),
                messageType: 'text',
            };
            setMessages(prev => [...prev, errorMessage]);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            <Header />
            <main className="container mx-auto px-4 py-8">
                <div className="max-w-7xl mx-auto">
                    <ChatWindow
                        messages={messages}
                        onSendMessage={handleSendMessage}
                    />
                </div>
            </main>
        </div>
    );
}

export default ChatPage;
