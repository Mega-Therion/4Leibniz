/**
 * The fixed atmospheric layer: obsidian-indigo wash, faint star-chart grid,
 * and a slow gold horizon glow. Sits behind all content (-z-10).
 */
export function AmbientGrid() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      {/* deep indigo wash */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(1200px 700px at 18% -10%, rgba(29, 33, 56, 0.55), transparent 60%), radial-gradient(900px 600px at 85% 15%, rgba(77, 70, 143, 0.16), transparent 60%), radial-gradient(1100px 800px at 50% 115%, rgba(139, 106, 43, 0.07), transparent 55%)',
        }}
      />
      {/* star-chart graticule */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            'linear-gradient(rgba(201, 194, 176, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(201, 194, 176, 0.035) 1px, transparent 1px)',
          backgroundSize: '72px 72px',
          maskImage:
            'radial-gradient(ellipse 90% 70% at 50% 0%, black 40%, transparent 100%)',
          WebkitMaskImage:
            'radial-gradient(ellipse 90% 70% at 50% 0%, black 40%, transparent 100%)',
        }}
      />
      {/* scattered stars */}
      <div
        className="absolute inset-0 animate-pulse-soft"
        style={{
          backgroundImage:
            'radial-gradient(1px 1px at 12% 22%, rgba(243, 239, 227, 0.5), transparent 100%), radial-gradient(1px 1px at 68% 8%, rgba(212, 169, 74, 0.4), transparent 100%), radial-gradient(1.5px 1.5px at 84% 32%, rgba(243, 239, 227, 0.35), transparent 100%), radial-gradient(1px 1px at 33% 46%, rgba(124, 114, 255, 0.4), transparent 100%), radial-gradient(1px 1px at 55% 15%, rgba(243, 239, 227, 0.3), transparent 100%), radial-gradient(1.5px 1.5px at 92% 60%, rgba(212, 169, 74, 0.3), transparent 100%)',
        }}
      />
      {/* vignette */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 140% 100% at 50% 50%, transparent 60%, rgba(8, 9, 13, 0.7) 100%)',
        }}
      />
    </div>
  );
}
