import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = '4Leibniz — a living archive of Leibniz';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          justifyContent: 'center',
          background: '#08090d',
          padding: '80px',
          position: 'relative',
        }}
      >
        {/* indigo wash — flat, satori-safe */}
        <div
          style={{
            position: 'absolute',
            top: -200,
            left: -150,
            width: 900,
            height: 700,
            borderRadius: '50%',
            background: '#131a2e',
            display: 'flex',
          }}
        />
        {/* gold orbital instrument */}
        <div
          style={{
            position: 'absolute',
            top: 60,
            right: -80,
            width: 520,
            height: 520,
            borderRadius: '50%',
            border: '2px solid rgba(212,169,74,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: 400,
              height: 400,
              borderRadius: '50%',
              border: '2px dashed rgba(212,169,74,0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div
              style={{
                width: 280,
                height: 280,
                borderRadius: '50%',
                border: '2px solid rgba(124,114,255,0.28)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div
                style={{
                  width: 90,
                  height: 90,
                  borderRadius: '50%',
                  border: '3px solid rgba(212,169,74,0.85)',
                  display: 'flex',
                }}
              />
            </div>
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            fontSize: 30,
            color: '#8e8a80',
            letterSpacing: 8,
            marginBottom: 20,
          }}
        >
          A LIVING ARCHIVE · EST. MMXXVI
        </div>
        <div
          style={{
            display: 'flex',
            fontSize: 150,
            color: '#f3efe3',
            fontFamily: 'Georgia, serif',
            lineHeight: 1,
          }}
        >
          4Leibniz
        </div>
        <div
          style={{
            display: 'flex',
            fontSize: 42,
            color: '#d4a94a',
            fontFamily: 'Georgia, serif',
            fontStyle: 'italic',
            marginTop: 26,
          }}
        >
          Transcribed. Translated. Searchable. Guided.
        </div>
        <div
          style={{
            position: 'absolute',
            bottom: 70,
            display: 'flex',
            width: 240,
            height: 3,
            background: '#8b6a2b',
          }}
        />
      </div>
    ),
    { ...size },
  );
}
