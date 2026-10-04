'use client';

import { GuideSourcesDrawer } from '@/components/GuideSourcesDrawer';
import type { GuideMode, GuideSource } from '@/lib/types';

const MODE_META: Record<GuideMode, { label: string; hint: string; cls: string }> = {
  corpus: {
    label: 'Corpus',
    hint: 'Answer grounded in retrieved archive texts.',
    cls: 'chip-gold',
  },
  dossier: {
    label: 'Dossier',
    hint: 'Answer grounded in editorial background.',
    cls: 'chip-violet',
  },
  mixed: {
    label: 'Mixed',
    hint: 'Answer grounded in texts and editorial background.',
    cls: 'chip-gold',
  },
  insufficient_evidence: {
    label: 'Insufficient evidence',
    hint: 'Retrieved sources were insufficient — the guide says so rather than inventing.',
    cls: '',
  },
};

export function ModeBadge({ mode }: { mode: GuideMode }) {
  const meta = MODE_META[mode] ?? MODE_META.insufficient_evidence;
  return (
    <span className={`chip ${meta.cls}`} title={meta.hint} aria-label={meta.hint}>
      {meta.label}
    </span>
  );
}

interface GuideMessageProps {
  role: 'user' | 'assistant';
  content: string;
  mode?: GuideMode;
  sources?: GuideSource[];
  isStreaming?: boolean;
}

export function GuideMessage({ role, content, mode, sources, isStreaming }: GuideMessageProps) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="panel-flat max-w-[85%] border-gold2/40 px-s4 py-s3 text-sm text-text1">
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start gap-s3">
      <div className="flex items-center gap-2">
        <span className="serif-heading text-sm text-gold1">Guide</span>
        {mode && <ModeBadge mode={mode} />}
      </div>
      <div className="max-w-[95%]">
        {content ? (
          <div className="space-y-s3 text-sm leading-[1.8] text-text2">
            {content
              .split(/\n{2,}/)
              .filter(Boolean)
              .map((paragraph, i) => (
                <p key={i} className="whitespace-pre-wrap">
                  {paragraph}
                </p>
              ))}
          </div>
        ) : isStreaming ? (
          <div className="flex items-center gap-s3" aria-label="The guide is thinking">
            <span className="skeleton h-2.5 w-40" />
            <span className="skeleton h-2.5 w-24" />
          </div>
        ) : null}
        {isStreaming && content && (
          <span
            className="ml-0.5 inline-block h-4 w-[2px] animate-pulse bg-gold1 align-middle"
            aria-hidden="true"
          />
        )}
        {sources && sources.length > 0 && <GuideSourcesDrawer sources={sources} />}
      </div>
    </div>
  );
}
