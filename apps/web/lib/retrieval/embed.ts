import { embed, embedMany } from 'ai';
import { embedModel } from '@/lib/ai/providers';
import { env } from '@/lib/config';

/** Embed a single query string. */
export async function embedQuery(query: string): Promise<number[]> {
  const { embedding } = await embed({
    model: embedModel(),
    value: query.slice(0, 4000),
    providerOptions: {
      openai: { dimensions: env.embeddingDimensions },
    },
  });
  return embedding;
}

/** Embed a batch of texts for ingestion (chunked to respect provider batch limits). */
export async function embedBatch(texts: string[]): Promise<number[][]> {
  const BATCH_SIZE = 80;
  const all: number[][] = [];
  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const slice = texts.slice(i, i + BATCH_SIZE).map((t) => t.slice(0, 4000));
    const { embeddings } = await embedMany({
      model: embedModel(),
      values: slice,
      providerOptions: {
        openai: { dimensions: env.embeddingDimensions },
      },
    });
    all.push(...embeddings);
  }
  return all;
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
