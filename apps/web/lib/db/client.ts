import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

let client: ReturnType<typeof postgres> | null = null;

/** Raw postgres.js client (lazy singleton). Throws only when actually used. */
export function pg() {
  const url = process.env.POSTGRES_URL;
  if (!url) {
    throw new Error('POSTGRES_URL is not configured — retrieval and ingestion are unavailable.');
  }
  if (!client) {
    client = postgres(url, { max: 10 });
  }
  return client;
}

/** Drizzle instance (lazy singleton). */
export function db() {
  return drizzle(pg(), { schema });
}

export function hasPostgres(): boolean {
  return Boolean(process.env.POSTGRES_URL);
}
