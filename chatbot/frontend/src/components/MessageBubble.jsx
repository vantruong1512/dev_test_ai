import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { vi } from 'date-fns/locale';
import { Bot, User } from 'lucide-react';

export default function MessageBubble({ message }) {
  const { role, text, ts } = message;
  const isUser = role === 'user';
  const isSystem = role === 'system';

  const timeAgo = ts ? formatDistanceToNow(new Date(ts), { 
    addSuffix: true, 
    locale: vi 
  }) : '';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-2`}>
      {!isUser && (
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isSystem ? 'bg-yellow-400' : 'bg-gradient-to-br from-blue-500 to-purple-600'
        }`}>
          {isSystem ? (
            <span className="text-white text-sm">⚠️</span>
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>
      )}
      
      <div className="max-w-[75%]">
        <div
          className={`rounded-2xl px-4 py-3 shadow-md ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-sm'
              : isSystem
              ? 'bg-yellow-100 text-yellow-900 border border-yellow-300'
              : 'bg-white text-gray-900 rounded-tl-sm'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed break-words">{text}</p>
        </div>
        {timeAgo && (
          <p className={`text-xs mt-1 ${
            isUser ? 'text-gray-400 text-right' : 'text-gray-400'
          }`}>
            {timeAgo}
          </p>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
}
