/**
 * Corpus ingestion — full reindex.
 *
 * Usage:  POSTGRES_URL=... AI_GATEWAY_API_KEY=... npm run ingest
 *
 * Requires the pgvector extension on the target database:
 *   CREATE EXTENSION IF NOT EXISTS vector;
 * and the Drizzle migrations applied:
 *   npm run db:generate && npm run db:migrate
 */
import { runIngestion } from '@/lib/ingest';

async function main() {
  if (!process.env.POSTGRES_URL) {
    console.error('✖ POSTGRES_URL is required.');
    process.exit(1);
  }
  if (!process.env.AI_GATEWAY_API_KEY) {
    console.error('✖ AI_GATEWAY_API_KEY is required.');
    process.exit(1);
  }

  console.log('⧫ 4Leibniz ingestion — beginning full reindex…');
  const report = await runIngestion();
  console.log('⧫ Ingestion complete.');
  console.log(`   works:            ${report.works}`);
  console.log(`   sections:         ${report.sections}`);
  console.log(`   chunks (indexed): ${report.chunks}`);
  console.log(`   themes:           ${report.themes}`);
  console.log(`   entities:         ${report.entities}`);
  console.log(`   dossier entries:  ${report.dossierEntries}`);
  process.exit(0);
}

main().catch((error) => {
  console.error('✖ Ingestion failed:', error);
  process.exit(1);
});
