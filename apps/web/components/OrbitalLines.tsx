/**
 * Slow-rotating orbital lines — the observatory signature. Pure SVG,
 * hairline gold and violet ellipses on a shared focus.
 */
export function OrbitalLines({ className = '' }: { className?: string }) {
  return (
    <div aria-hidden="true" className={`pointer-events-none ${className}`}>
      <svg
        viewBox="0 0 800 800"
        fill="none"
        className="h-full w-full"
        style={{ maxWidth: 'none' }}
      >
        <g className="animate-orbit-slow" style={{ transformOrigin: '400px 400px' }}>
          <ellipse
            cx="400"
            cy="400"
            rx="360"
            ry="150"
            stroke="rgba(212,169,74,0.30)"
            strokeWidth="0.7"
          />
          <ellipse
            cx="400"
            cy="400"
            rx="290"
            ry="290"
            stroke="rgba(212,169,74,0.14)"
            strokeWidth="0.5"
            strokeDasharray="3 7"
          />
          <circle cx="760" cy="400" r="2.4" fill="rgba(212,169,74,0.85)" />
          <circle cx="400" cy="550" r="1.6" fill="rgba(124,114,255,0.7)" />
        </g>
        <g className="animate-orbit-rev" style={{ transformOrigin: '400px 400px' }}>
          <ellipse
            cx="400"
            cy="400"
            rx="330"
            ry="95"
            stroke="rgba(124,114,255,0.22)"
            strokeWidth="0.7"
          />
          <circle cx="730" cy="400" r="1.8" fill="rgba(124,114,255,0.8)" />
        </g>
        <circle cx="400" cy="400" r="3" fill="rgba(212,169,74,0.9)" />
        <circle
          cx="400"
          cy="400"
          r="14"
          stroke="rgba(212,169,74,0.35)"
          strokeWidth="0.8"
        />
        <circle
          cx="400"
          cy="400"
          r="30"
          stroke="rgba(212,169,74,0.16)"
          strokeWidth="0.6"
          strokeDasharray="2 5"
        />
      </svg>
    </div>
  );
}
