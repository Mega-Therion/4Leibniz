import type { TimelineEvent } from '@/lib/types';

const CATEGORY_META: Record<
  TimelineEvent['category'],
  { label: string; dot: string }
> = {
  life: { label: 'Life', dot: 'bg-gold1' },
  work: { label: 'Work', dot: 'bg-violet1' },
  science: { label: 'Science', dot: 'bg-teal1' },
  diplomacy: { label: 'Diplomacy', dot: 'bg-text2' },
  legacy: { label: 'Legacy', dot: 'bg-gold2' },
};

/** A vertical rail of years — gold dots, hairline track, steady rhythm. */
export function TimelineRail({ events }: { events: TimelineEvent[] }) {
  return (
    <div className="relative">
      <div
        aria-hidden="true"
        className="absolute bottom-2 left-[7px] top-2 w-px bg-line1"
      />
      <ol className="flex flex-col gap-s8">
        {events.map((event) => {
          const meta = CATEGORY_META[event.category] ?? CATEGORY_META.life;
          return (
            <li key={event.slug} className="relative pl-s8">
              <span
                aria-hidden="true"
                className={`absolute left-0 top-[9px] h-[15px] w-[15px] rounded-full border-2 border-bg0 ${meta.dot}`}
              />
              <div className="flex flex-wrap items-baseline gap-x-s3 gap-y-1">
                <span className="font-mono text-sm text-gold1">{event.dateLabel}</span>
                <span className="chip !py-0.5 !text-[10px]">{meta.label}</span>
              </div>
              <h3 className="serif-heading mt-s2 text-xl text-text1">{event.title}</h3>
              <p className="mt-s2 max-w-2xl text-sm leading-relaxed text-text2">
                {event.description}
              </p>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
