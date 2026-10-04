'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useChat } from 'ai/react';
import Link from 'next/link';
import { GuideMessage } from '@/components/GuideMessage';
import type { GuideData } from '@/lib/types';

function extractGuideData(data: unknown): GuideData[] {
  if (!Array.isArray(data)) return [];
  const found: GuideData[] = [];
  for (const entry of data) {
    if (
      entry &&
      typeof entry === 'object' &&
      'sources' in entry &&
      'mode' in entry
    ) {
      found.push(entry as GuideData);
    }
  }
  return found;
}

const GENERAL_PROMPTS = [
  'What concepts recur across the translated works?',
  'Summarize the Discourse on Metaphysics in plain language.',
  'How does the Monadology relate to the Discourse on Metaphysics?',
  'Who was Leibniz corresponding with around 1686?',
  'What does Leibniz argue about substance?',
  'Why does Leibniz say this is the best of all possible worlds?',
];

export function GuidePanel({
  workSlug,
  workTitle,
  initialInput,
}: {
  workSlug: string | null;
  workTitle: string | null;
  initialInput?: string;
}) {
  const sessionRef = useRef<string>(
    typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : '',
  );
  const [followups, setFollowups] = useState<string[]>([]);

  const { messages, input, handleInputChange, handleSubmit, isLoading, stop, error, data, reload } =
    useChat({
      body: {
        workSlug,
        sessionId: sessionRef.current,
      },
      initialInput,
    });

  // zip streamed data payloads to assistant messages, in order
  const guideData = useMemo(() => extractGuideData(data), [data]);
  const assistantData = useMemo(() => {
    let i = 0;
    const map = new Map<string, GuideData>();
    for (const m of messages) {
      if (m.role === 'assistant') {
        map.set(m.id, guideData[i] ?? null);
        i += 1;
      }
    }
    return map;
  }, [messages, guideData]);

  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant');
  const lastFollowups = lastAssistant
    ? assistantData.get(lastAssistant.id)?.suggestedFollowups
    : undefined;
  useEffect(() => {
    if (lastFollowups) setFollowups(lastFollowups);
  }, [lastFollowups]);

  const suggested = useMemo(() => {
    const base = workTitle
      ? [
          `What does Leibniz argue here, in plain language?`,
          `Summarize ${workTitle} in one page.`,
          `What role does this work play in Leibniz's system?`,
        ]
      : GENERAL_PROMPTS;
    return base;
  }, [workTitle]);

  const showSuggestions = messages.length <= 1;

  return (
    <div className="flex min-h-[70vh] flex-col">
      {/* scope banner */}
      {workSlug && (
        <div className="panel-flat mb-s6 flex flex-wrap items-center justify-between gap-s3 border-gold2/40 px-s4 py-s3">
          <p className="text-sm text-text2">
            Scoped to{' '}
            <Link
              href={`/works/${workSlug}`}
              className="text-gold1 underline decoration-gold2 underline-offset-4"
            >
              {workTitle}
            </Link>
            . The guide reads this work first, then widens to the archive.
          </p>
          <Link href="/guide" className="label hover:text-gold1">
            Clear scope →
          </Link>
        </div>
      )}

      {/* transcript */}
      <div className="flex-1 space-y-s8 overflow-y-auto py-s2">
        {messages.length === 0 && (
          <div className="panel flex flex-col items-center gap-s4 p-s8 text-center">
            <span className="serif-heading text-3xl text-text1">
              Ask the archive.
            </span>
            <p className="max-w-md text-sm leading-relaxed text-text3">
              Every answer is retrieval-grounded in the texts and the editorial
              dossier, with sources you can open and verify. The guide will
              tell you plainly when the evidence runs out.
            </p>
          </div>
        )}
        {messages.map((m) => {
          const gd = m.role === 'assistant' ? assistantData.get(m.id) : null;
          return (
            <GuideMessage
              key={m.id}
              role={m.role as 'user' | 'assistant'}
              content={m.content}
              mode={gd?.mode}
              sources={gd?.sources}
              isStreaming={isLoading && m.id === messages[messages.length - 1]?.id}
            />
          );
        })}
        {error && (
          <div className="panel-flat border-danger1/40 p-s4 text-sm text-danger1" role="alert">
            <p>The guide could not answer: {(error as Error).message ?? 'stream error'}</p>
            <button
              type="button"
              onClick={() => reload()}
              className="btn-ghost mt-s3 !px-4 !py-1.5 text-xs"
            >
              Retry
            </button>
          </div>
        )}
      </div>

      {/* followups + suggestions */}
      <div className="mt-s4">
        {showSuggestions && (
          <div className="flex flex-wrap gap-2" aria-label="Suggested questions">
            {suggested.map((q) => (
              <button
                key={q}
                type="button"
                className="chip transition-colors hover:border-gold1 hover:text-text1"
                onClick={() => {
                  const synthetic = { target: { value: q } } as never;
                  handleInputChange(synthetic);
                  setTimeout(() => {
                    const form = document.getElementById('guide-form') as HTMLFormElement | null;
                    form?.requestSubmit();
                  }, 0);
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
        {!showSuggestions && followups.length > 0 && (
          <div className="flex flex-wrap gap-2" aria-label="Suggested follow-ups">
            {followups.map((q) => (
              <button
                key={q}
                type="button"
                className="chip transition-colors hover:border-gold1 hover:text-text1"
                onClick={() => {
                  const synthetic = { target: { value: q } } as never;
                  handleInputChange(synthetic);
                  setTimeout(() => {
                    const form = document.getElementById('guide-form') as HTMLFormElement | null;
                    form?.requestSubmit();
                  }, 0);
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* sticky input */}
      <form
        id="guide-form"
        onSubmit={handleSubmit}
        className="panel sticky bottom-4 mt-s4 flex items-end gap-s3 p-s3"
      >
        <label htmlFor="guide-input" className="sr-only">
          Ask the guide a question
        </label>
        <textarea
          id="guide-input"
          rows={1}
          value={input}
          onChange={handleInputChange}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder={
            workTitle
              ? `Ask about ${workTitle}…`
              : 'Ask about Leibniz — the texts, the concepts, the life…'
          }
          className="max-h-40 flex-1 resize-none bg-transparent px-s3 py-s2 text-sm text-text1 placeholder:text-text3 focus:outline-none"
          disabled={isLoading}
        />
        {isLoading ? (
          <button type="button" onClick={stop} className="btn-ghost !px-4 !py-1.5 text-xs">
            Stop
          </button>
        ) : (
          <button type="submit" className="btn-gold !px-5 !py-1.5 text-xs" disabled={!input.trim()}>
            Ask
          </button>
        )}
      </form>
      <p className="mt-s2 text-center text-[11px] text-text3">
        Answers are grounded in retrieved sources but can be wrong — open the
        citations and verify.
      </p>
    </div>
  );
}
