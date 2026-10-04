import clsx from 'clsx';
import type { ReactNode } from 'react';

interface ThemeBadgeProps {
  label: ReactNode;
  variant?: 'gold' | 'violet' | 'plain';
  className?: string;
}

/** A small thematic tag — links when wrapped in a link by the caller. */
export function ThemeBadge({ label, variant = 'plain', className }: ThemeBadgeProps) {
  return (
    <span
      className={clsx(
        'chip',
        variant === 'gold' && 'chip-gold',
        variant === 'violet' && 'chip-violet',
        className,
      )}
    >
      {label}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { label: string; variant: 'gold' | 'violet' | 'plain' }> = {
    translated: { label: 'Translated', variant: 'gold' },
    transcribed: { label: 'Transcribed', variant: 'gold' },
    completed: { label: 'Completed edition', variant: 'gold' },
    'in-progress': { label: 'In progress', variant: 'violet' },
  };
  const entry = map[status] ?? { label: status, variant: 'plain' as const };
  return (
    <ThemeBadge label={entry.label} variant={entry.variant} />
  );
}
