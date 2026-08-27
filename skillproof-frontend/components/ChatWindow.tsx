// Task 11: Multi-turn chat window with message history and input field
'use client';

import type { ChatMessage } from '@/lib/types';

interface ChatWindowProps {
  messages?: ChatMessage[];
  targetRoleId?: number;
  onSend?: (message: string) => void;
}

export default function ChatWindow({ messages = [], onSend }: ChatWindowProps) {
  return (
    <div className="flex flex-col gap-4 rounded-lg border p-4">
      <h2 className="text-lg font-semibold">Chat</h2>
      <div className="flex-1 space-y-2">
        {messages.map((msg) => (
          <div key={msg.id} className={`text-sm ${msg.role === 'assistant' ? 'text-blue-700' : 'text-gray-800'}`}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        ))}
      </div>
      {/* Full implementation with input form in Task 11 */}
    </div>
  );
}
