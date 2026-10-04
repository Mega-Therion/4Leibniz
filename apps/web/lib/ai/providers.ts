import { createOpenAI } from '@ai-sdk/openai';
import { env } from '@/lib/config';

/**
 * All model traffic flows through the Vercel AI Gateway using OpenAI-compatible
 * identifiers (e.g. "openai/gpt-4o-mini", "anthropic/claude-sonnet-4-20250514").
 * Swap providers by changing CHAT_MODEL / EMBEDDING_MODEL — no code changes.
 */
export const gateway = createOpenAI({
  baseURL: env.aiGatewayBaseUrl,
  apiKey: env.aiGatewayApiKey,
});

export function chatModel() {
  return gateway(env.chatModel);
}

export function embedModel() {
  return gateway.embedding(env.embeddingModel);
}
