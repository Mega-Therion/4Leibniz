import { embed, embedMany } from 'ai';
import { embedModel } from '@/lib/ai/providers';
import { env } from '@/lib/config';

/** Embed a single query string. */
export async function embedQuery(query: string): Promise<number[]> {
  const { embedding } = await embed({
    model: embedModel(),
    value: query.slice(0, 4000),
  });
  return embedding;
}

/** Embed a batch of texts for ingestion. */
export async function embedBatch(texts: string[]): Promise<number[][]> {
  const { embeddings } = await embedMany({
    model: embedModel(),
    values: texts.map((t) => t.slice(0, 4000)),
  });
  return embeddings;
}

export function vectorLiteral(embedding: number[]): string {
  return JSON.stringify(embedding);
}

export function chunkTokenEstimate(text: string): number {
  return Math.ceil(text.length / 4);
}

export function isConfigured(): boolean {
  return Boolean(env.postgresUrl && env.aiGatewayApiKey);
}
