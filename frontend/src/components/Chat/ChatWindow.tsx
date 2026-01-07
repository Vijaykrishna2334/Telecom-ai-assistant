import React, { useEffect, useRef, useState } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import type { Message } from '../../types';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, onSendMessage }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showRagPanel, setShowRagPanel] = useState(true);
  const [selectedContext, setSelectedContext] = useState<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    // Auto-select latest RAG context
    const lastAssistantMsg = [...messages].reverse().find(m => m.role === 'assistant' && m.ragContext);
    if (lastAssistantMsg?.ragContext) {
      console.log('📚 RAG Context received:', lastAssistantMsg.ragContext.substring(0, 200) + '...');
      setSelectedContext(lastAssistantMsg.ragContext);
    }
  }, [messages]);

  return (
    <div className="flex gap-4" style={{ minWidth: '900px' }}>
      {/* Chat Panel */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md flex-1 h-[600px] flex flex-col" style={{ minWidth: showRagPanel ? '500px' : '100%' }}>
        <div className="flex justify-between items-center p-3 border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900">
          <span className="text-sm font-bold text-blue-700 dark:text-blue-300">💬 JioCare Chat</span>
          <button
            onClick={() => setShowRagPanel(!showRagPanel)}
            className="text-xs px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 font-medium"
          >
            {showRagPanel ? '🔍 Hide RAG Panel' : '🔍 Show RAG Panel'}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} onClick={() => message.ragContext && setSelectedContext(message.ragContext)}>
              <MessageBubble message={message} />
              {message.ragContext && (
                <div className="text-xs text-green-600 dark:text-green-400 ml-2 cursor-pointer hover:underline font-medium">
                  📚 RAG data available - click to view
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <ChatInput onSendMessage={onSendMessage} />
        </div>
      </div>

      {/* RAG Context Side Panel */}
      {showRagPanel && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md h-[600px] flex flex-col border-l-4 border-green-500" style={{ width: '400px', minWidth: '350px' }}>
          <div className="p-3 border-b border-gray-200 dark:border-gray-700 bg-green-100 dark:bg-green-900">
            <span className="text-sm font-bold text-green-800 dark:text-green-200">🔍 RAG Context (Debug)</span>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">Shows what data is sent to LLM</p>
          </div>
          <div className="flex-1 overflow-y-auto p-3 bg-gray-50 dark:bg-gray-900">
            {selectedContext ? (
              <div>
                <div className="text-xs text-gray-500 mb-2">📄 Retrieved Knowledge Base Data:</div>
                <pre className="text-xs whitespace-pre-wrap text-gray-800 dark:text-gray-200 font-mono bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-700">
                  {selectedContext}
                </pre>
              </div>
            ) : (
              <div className="text-center mt-20">
                <div className="text-4xl mb-4">📭</div>
                <p className="text-sm text-gray-500 dark:text-gray-400">No RAG context yet</p>
                <p className="text-xs text-gray-400 mt-2">Send a message to see what data RAG retrieves from knowledge base</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
