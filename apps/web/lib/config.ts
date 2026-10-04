// ─── Centralized environment handling ─────────────────────────────────────
// All env access funnels through here. Vercel: set these in Project → Settings
// → Environment Variables (see .env.example).

function num(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export const env = {
  postgresUrl: process.env.POSTGRES_URL ?? '',
  aiGatewayApiKey: process.env.AI_GATEWAY_API_KEY ?? '',
  aiGatewayBaseUrl: process.env.AI_GATEWAY_BASE_URL ?? 'https://ai-gateway.vercel.sh/v1',
  chatModel: process.env.CHAT_MODEL ?? 'openai/gpt-4o-mini',
  embeddingModel: process.env.EMBEDDING_MODEL ?? 'openai/text-embedding-3-small',
  embeddingDimensions: num(process.env.EMBEDDING_DIMENSIONS, 1536),
  retrievalLimit: num(process.env.RETRIEVAL_LIMIT, 6),
  workScopeLimit: num(process.env.WORK_SCOPE_LIMIT, 4),
  ingestSecret: process.env.INGEST_SECRET ?? '',
  siteUrl: process.env.NEXT_PUBLIC_SITE_URL ?? 'https://4leibniz.vercel.app',
} as const;

export function isRetrievalConfigured(): boolean {
  return Boolean(env.postgresUrl && env.aiGatewayApiKey);
}
