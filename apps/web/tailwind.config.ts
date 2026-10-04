import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg0: 'var(--bg-0)',
        bg1: 'var(--bg-1)',
        bg2: 'var(--bg-2)',
        surface1: 'var(--surface-1)',
        surface2: 'var(--surface-2)',
        surface3: 'var(--surface-3)',
        text1: 'var(--text-1)',
        text2: 'var(--text-2)',
        text3: 'var(--text-3)',
        gold1: 'var(--gold-1)',
        gold2: 'var(--gold-2)',
        violet1: 'var(--violet-1)',
        violet2: 'var(--violet-2)',
        teal1: 'var(--teal-1)',
        danger1: 'var(--danger-1)',
        line1: 'var(--border-1)',
        line2: 'var(--border-2)',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        shadow1: 'var(--shadow-1)',
        shadow2: 'var(--shadow-2)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
      spacing: {
        s1: 'var(--space-1)',
        s2: 'var(--space-2)',
        s3: 'var(--space-3)',
        s4: 'var(--space-4)',
        s6: 'var(--space-6)',
        s8: 'var(--space-8)',
        s12: 'var(--space-12)',
        s16: 'var(--space-16)',
      },
      maxWidth: {
        archive: '1180px',
        reader: '820px',
      },
      animation: {
        'orbit-slow': 'orbit 140s linear infinite',
        'orbit-rev': 'orbit 190s linear infinite reverse',
        'pulse-soft': 'pulseSoft 7s ease-in-out infinite',
        'rise-in': 'riseIn 1s cubic-bezier(0.22, 1, 0.36, 1) both',
      },
      keyframes: {
        orbit: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.35' },
          '50%': { opacity: '0.7' },
        },
        riseIn: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
