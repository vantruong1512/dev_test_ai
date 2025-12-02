import React from 'react';

export default function ModeBadge({ mode }) {
  const isAI = mode === 'AI_ONLY';

  return (
    <div
      className={`px-2 py-0.5 rounded-full text-xs font-medium ${
        isAI
          ? 'bg-white/20 text-white'
          : 'bg-yellow-400 text-yellow-900'
      }`}
    >
      {isAI ? '🤖 AI' : '👤 Human'}
    </div>
  );
}
