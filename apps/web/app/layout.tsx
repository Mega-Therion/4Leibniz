import type { Metadata, Viewport } from 'next';
import { Instrument_Serif, Inter } from 'next/font/google';
import '@/styles/globals.css';
import { AmbientGrid } from '@/components/AmbientGrid';
import { SiteHeader } from '@/components/SiteHeader';
import { SiteFooter } from '@/components/SiteFooter';
import { env } from '@/lib/config';

const display = Instrument_Serif({
  weight: '400',
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

const sans = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const description =
  'A living archive of Leibniz: transcribed, translated, searchable — with a source-grounded AI guide. Read the Discourse on Metaphysics and the Monadology with citations, context, and an AI guide grounded in the texts.';

export const metadata: Metadata = {
  metadataBase: new URL(env.siteUrl),
  title: {
    default: '4Leibniz — A living archive of Leibniz',
    template: '%s — 4Leibniz',
  },
  description,
  applicationName: '4Leibniz',
  keywords: [
    'Leibniz',
    'monadology',
    'discourse on metaphysics',
    'philosophy archive',
    'AI reading guide',
    'scholarly edition',
  ],
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    siteName: '4Leibniz',
    title: '4Leibniz — A living archive of Leibniz',
    description,
    url: '/',
  },
  twitter: {
    card: 'summary_large_image',
    title: '4Leibniz — A living archive of Leibniz',
    description,
  },
};

export const viewport: Viewport = {
  themeColor: '#08090d',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body className="min-h-screen bg-bg0 font-sans antialiased">
        <AmbientGrid />
        <SiteHeader />
        <main id="main" className="relative">
          {children}
        </main>
        <SiteFooter />
      </body>
    </html>
  );
}
