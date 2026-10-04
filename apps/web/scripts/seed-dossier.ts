/**
 * Dossier-only reseed — biography, timeline, concepts, correspondents, themes.
 *
 * Usage:  POSTGRES_URL=... AI_GATEWAY_API_KEY=... npm run seed:dossier
 */
import { seedDossier } from '@/lib/ingest';

async function main() {
  if (!process.env.POSTGRES_URL || !process.env.AI_GATEWAY_API_KEY) {
    console.error('✖ POSTGRES_URL and AI_GATEWAY_API_KEY are required.');
    process.exit(1);
  }

  console.log('⧫ 4Leibniz — reseeding editorial dossier…');
  const count = await seedDossier();
  console.log(`⧫ Done. ${count} dossier entries embedded and stored.`);
  process.exit(0);
}

main().catch((error) => {
  console.error('✖ Dossier seed failed:', error);
  process.exit(1);
});
