import type { ReactNode } from 'react';

interface SectionFrameProps {
  id?: string;
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  children: ReactNode;
  align?: 'left' | 'center';
  className?: string;
}

/**
 * The recurring editorial section: eyebrow label, serif title, gold rule,
 * optional description, then content. Gives the whole site one rhythm.
 */
export function SectionFrame({
  id,
  eyebrow,
  title,
  description,
  children,
  align = 'left',
  className = '',
}: SectionFrameProps) {
  return (
    <section id={id} className={`mx-auto max-w-archive px-s6 ${className}`}>
      <header className={align === 'center' ? 'text-center' : ''}>
        <p className="label">{eyebrow}</p>
        <h2 className="serif-heading mt-s3 text-3xl sm:text-4xl">{title}</h2>
        <div
          className={`gold-rule mt-s4 ${align === 'center' ? 'mx-auto w-24' : 'w-24'}`}
        />
        {description && (
          <p
            className={`mt-s4 text-base leading-relaxed text-text2 ${
              align === 'center' ? 'mx-auto' : ''
            } max-w-2xl`}
          >
            {description}
          </p>
        )}
      </header>
      <div className="mt-s8">{children}</div>
    </section>
  );
}
