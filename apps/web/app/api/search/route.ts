import { searchArchive } from '@/lib/retrieval/retrieve';
import { isConfigured } from '@/lib/retrieval/embed';

export const runtime = 'nodejs';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const q = (searchParams.get('q') ?? '').trim();
  const work = searchParams.get('work');
  const limit = Math.min(Number(searchParams.get('limit') ?? 8) || 8, 20);

  if (q.length < 2) {
    return Response.json({ error: 'Query too short — provide at least 2 characters.' }, { status: 400 });
  }
  if (!isConfigured()) {
    return Response.json(
      { error: 'Semantic search is not configured. Set POSTGRES_URL and AI_GATEWAY_API_KEY.' },
      { status: 503 },
    );
  }

  try {
    const results = await searchArchive(q, work, limit);
    return Response.json({
      query: q,
      scopedTo: work,
      count: results.length,
      results,
    });
  } catch (error) {
    console.error('[search] failed:', error);
    return Response.json({ error: 'Search failed — see server logs.' }, { status: 500 });
  }
}
