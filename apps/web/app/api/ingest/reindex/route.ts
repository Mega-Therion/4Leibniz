import { runIngestion } from '@/lib/ingest';
import { env } from '@/lib/config';

export const runtime = 'nodejs';
export const maxDuration = 60;

/**
 * Protected full-corpus reindex endpoint.
 *
 *   curl -X POST https://<site>/api/ingest/reindex \
 *        -H "Authorization: Bearer $INGEST_SECRET"
 *
 * Disabled unless INGEST_SECRET is set. For large corpora prefer local:
 *   npm run ingest
 */
export async function POST(req: Request) {
  if (!env.ingestSecret) {
    return Response.json(
      { error: 'Reindex endpoint is disabled (INGEST_SECRET not set).' },
      { status: 403 },
    );
  }
  const auth = req.headers.get('authorization') ?? '';
  if (auth !== `Bearer ${env.ingestSecret}`) {
    return Response.json({ error: 'Unauthorized.' }, { status: 401 });
  }
  if (!env.postgresUrl || !env.aiGatewayApiKey) {
    return Response.json(
      { error: 'POSTGRES_URL and AI_GATEWAY_API_KEY are required.' },
      { status: 503 },
    );
  }

  try {
    const report = await runIngestion();
    return Response.json({ ok: true, report });
  } catch (error) {
    console.error('[reindex] failed:', error);
    return Response.json(
      { error: 'Reindex failed.', detail: String(error) },
      { status: 500 },
    );
  }
}
