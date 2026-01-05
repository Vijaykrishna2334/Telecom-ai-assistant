import React from 'react';
import type { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs md:max-w-md lg:max-w-lg px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-none'
            : isSystem
            ? 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
            : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 shadow-md rounded-bl-none'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
        <span className={`text-xs ${isUser ? 'text-primary-100' : 'text-gray-500'} mt-1 block`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default MessageBubble;
