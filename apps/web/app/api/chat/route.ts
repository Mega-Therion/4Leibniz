import { convertToModelMessages, streamText } from 'ai';
import { chatModel } from '@/lib/ai/providers';
import { buildSystemPrompt, suggestedFollowups } from '@/lib/ai/system-prompt';
import {
  toUIMessage,
  textOfIncoming,
  type IncomingChatMessage,
} from '@/lib/ai/incoming-message';
import { retrieveContext } from '@/lib/retrieval/retrieve';
import { db } from '@/lib/db/client';
import * as t from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export const runtime = 'nodejs';
export const maxDuration = 60;

interface ChatRequestBody {
  messages?: IncomingChatMessage[];
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

  const incoming = (body.messages ?? [])
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-12);

  const lastUser = [...incoming].reverse().find((m) => m.role === 'user');
  const lastUserText = lastUser ? textOfIncoming(lastUser) : '';
  if (!lastUser || !lastUserText.trim()) {
    return new Response(JSON.stringify({ error: 'No user message found.' }), {
      status: 400,
      headers: { 'content-type': 'application/json' },
    });
  }

  const workSlug = body.workSlug ?? null;
  const retrieval = await retrieveContext(lastUserText, workSlug);
  const metadata = {
    mode: retrieval.mode,
    sources: retrieval.sources,
    suggestedFollowups: suggestedFollowups(retrieval.mode, retrieval.sources[0]?.title ?? null),
    scope: workSlug,
    degraded: retrieval.degraded !== 'ok' ? retrieval.degraded : undefined,
  };

  const system = buildSystemPrompt({
    mode: retrieval.mode,
    sources: retrieval.sources,
    scope: workSlug,
  });

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
        { sessionId, role: 'user', content: lastUserText },
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

  const result = streamText({
    model: chatModel(),
    system,
    messages: await convertToModelMessages(incoming.map(toUIMessage)),
    temperature: 0.4,
    maxOutputTokens: 1200,
    onFinish: ({ text }) => {
      void persist(text);
    },
  });

  return result.toUIMessageStreamResponse({
    messageMetadata: () => metadata,
  });
}
