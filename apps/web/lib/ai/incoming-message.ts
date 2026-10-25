import type { UIMessage } from 'ai';

export interface IncomingChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content?: string;
  parts?: { type: string; text?: string }[];
}

export function textOfIncoming(message: IncomingChatMessage): string {
  if (typeof message.content === 'string') return message.content;
  return (message.parts ?? [])
    .filter((part) => part.type === 'text' && typeof part.text === 'string')
    .map((part) => part.text as string)
    .join('');
}

export function toUIMessage(message: IncomingChatMessage): UIMessage {
  return {
    id: message.id ?? crypto.randomUUID(),
    role: message.role === 'assistant' ? 'assistant' : 'user',
    parts: [{ type: 'text', text: textOfIncoming(message) }],
  };
}

export function guideDataFromMessage(message: { metadata?: unknown }): {
  mode?: string;
  sources?: unknown;
  suggestedFollowups?: string[];
} | null {
  const meta = message.metadata;
  if (!meta || typeof meta !== 'object') return null;
  if (!('sources' in meta) || !('mode' in meta)) return null;
  return meta as {
    mode?: string;
    sources?: unknown;
    suggestedFollowups?: string[];
  };
}
