import { streamText, StreamData, type JSONValue } from 'ai';
import { chatModel } from '@/lib/ai/providers';
import { buildSystemPrompt, suggestedFollowups } from '@/lib/ai/system-prompt';
import { retrieveContext } from '@/lib/retrieval/retrieve';
import { db } from '@/lib/db/client';
import * as t from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export const runtime = 'nodejs';
export const maxDuration = 60;

interface ChatRequestBody {
  messages?: { role: 'user' | 'assistant' | 'system'; content: string }[];
  workSlug?: string | null;
  sessionId?: string | null;
}

export async function POST(req: Request) {
  let body: ChatRequestBody;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON body.' }), {
      status: 400,
      headers: { 'content-type': 'application/json' },
    });
  }

  const messages = (body.messages ?? [])
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-12); // keep the window bounded

  const lastUser = [...messages].reverse().find((m) => m.role === 'user');
  if (!lastUser) {
    return new Response(JSON.stringify({ error: 'No user message found.' }), {
      status: 400,
      headers: { 'content-type': 'application/json' },
    });
  }

  const workSlug = body.workSlug ?? null;

  // ── Retrieval-first context assembly (server-side only) ────────────────
  const retrieval = await retrieveContext(lastUser.content, workSlug);

  const data = new StreamData();
  data.append({
    mode: retrieval.mode,
    sources: retrieval.sources,
    suggestedFollowups: suggestedFollowups(
      retrieval.mode,
      retrieval.sources[0]?.title ?? null,
    ),
    scope: workSlug,
    degraded: retrieval.degraded !== 'ok' ? retrieval.degraded : undefined,
  } as unknown as JSONValue);
  data.close();

  const system = buildSystemPrompt({
    mode: retrieval.mode,
    sources: retrieval.sources,
    scope: workSlug,
  });

  const result = await streamText({
    model: chatModel(),
    system,
    messages,
    temperature: 0.4,
    maxTokens: 1200,
    onFinish: ({ text }) => {
      void persist(text);
    },
  });

  // best-effort transcript persistence — never block the stream on it
  const persist = async (answer: string) => {
    try {
      if (!process.env.POSTGRES_URL || !body.sessionId) return;
      const database = db();
      const [session] = await database
        .insert(t.chatSessions)
        .values({ id: body.sessionId, workSlug })
        .onConflictDoNothing()
        .returning({ id: t.chatSessions.id });
      const sessionId =
        session?.id ??
        (
          await database
            .select({ id: t.chatSessions.id })
            .from(t.chatSessions)
            .where(eq(t.chatSessions.id, body.sessionId!))
        )[0]?.id;
      if (!sessionId) return;
      await database.insert(t.chatMessages).values([
        { sessionId, role: 'user', content: lastUser.content },
        {
          sessionId,
          role: 'assistant',
          content: answer,
          mode: retrieval.mode,
          sources: retrieval.sources,
        },
      ]);
    } catch (error) {
      console.error('[chat] transcript persistence failed:', error);
    }
  };

  return result.toDataStreamResponse({ data });
}
