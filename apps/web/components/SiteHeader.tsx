'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import clsx from 'clsx';

const NAV = [
  { href: '/works', label: 'Archive' },
  { href: '/guide', label: 'Guide' },
  { href: '/catalog', label: 'Proofs' },
  { href: '/leibniz', label: 'Leibniz' },
  { href: '/about', label: 'About' },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) =>
    pathname === href || (href !== '/' && pathname.startsWith(href));

  return (
    <header className="sticky top-0 z-40">
      <div
        className="border-b border-line1 backdrop-blur-xl"
        style={{ background: 'rgba(8, 9, 13, 0.78)' }}
      >
        <div className="mx-auto flex max-w-archive items-center justify-between px-s6 py-s4">
          <Link
            href="/"
            className="group flex items-baseline gap-2"
            aria-label="4Leibniz home"
          >
            <span className="serif-heading text-2xl tracking-tight text-text1 group-hover:text-gold1">
              4Leibniz
            </span>
            <span className="hidden text-text3 sm:inline" aria-hidden="true">
              ·
            </span>
            <span className="label hidden sm:inline">A living archive</span>
          </Link>

          {/* desktop nav */}
          <nav aria-label="Primary" className="hidden items-center gap-7 md:flex">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  'text-sm tracking-wide transition-colors',
                  isActive(item.href)
                    ? 'text-gold1'
                    : 'text-text2 hover:text-text1',
                )}
                aria-current={isActive(item.href) ? 'page' : undefined}
              >
                {item.label}
              </Link>
            ))}
            <Link href="/guide" className="btn-gold !px-4 !py-1.5 text-xs">
              Ask the Guide
            </Link>
          </nav>

          {/* mobile toggle */}
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="flex h-10 w-10 items-center justify-center rounded-sm text-text2 md:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? 'Close menu' : 'Open menu'}
          >
            <span className="sr-only">{open ? 'Close menu' : 'Open menu'}</span>
            <svg width="18" height="14" viewBox="0 0 18 14" fill="none" aria-hidden="true">
              <path
                d={open ? 'M2 2l14 10M16 2L2 12' : 'M0 1h18M0 7h18M0 13h18'}
                stroke="currentColor"
                strokeWidth="1.4"
              />
            </svg>
          </button>
        </div>

        {open && (
          <nav
            id="mobile-nav"
            aria-label="Primary mobile"
            className="border-t border-line1 px-s6 py-s4 md:hidden"
          >
            <ul className="flex flex-col gap-4">
              {NAV.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className={clsx(
                      'text-base',
                      isActive(item.href) ? 'text-gold1' : 'text-text2',
                    )}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
              <li>
                <Link
                  href="/guide"
                  onClick={() => setOpen(false)}
                  className="btn-gold text-xs"
                >
                  Ask the Guide
                </Link>
              </li>
            </ul>
          </nav>
        )}
      </div>
    </header>
  );
}
