/**
 * WebFidelity.tsx — body scenes for "Half a Page." (what scrapers drop).
 *
 * Reel: books/webfidelity/youtube/half-a-page
 * Host: Param Madan · voice Kokoro af_bella
 *
 * CONTRACT (illustrations/kit.tsx): every scene is a pure function of useP().
 * No wall clock, no state, no CSS transitions.
 *
 * COLOR: claude palette, one terracotta moment per beat, always on the thing
 * that was lost or the number that matters.
 *
 * FACT NOTE: every figure comes from the author's own WebFidelity runs
 * (October 2026) and is ledgered in the reel's SOURCES.md. Firecrawl's
 * renderer can change; the reel dates its measurements.
 */
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { CLAUDE } from '../tokens/claude';
import { SAFE } from '../tokens/layout';
import { IlluStage, SERIF, SANS, MONO, remap, ease, useP } from '../illustrations/kit';

const INK = CLAUDE.INK;
const SOFT = CLAUDE.INK_SOFT;
const ACCENT = CLAUDE.SPARK;
const HAIR = CLAUDE.BORDER;
const CARD = CLAUDE.CARD;

const Eyebrow: React.FC<{ text: string; o: number }> = ({ text, o }) => (
  <div style={{ fontFamily: SANS, fontSize: 34, letterSpacing: 5, color: SOFT, textTransform: 'uppercase', opacity: o, textAlign: 'center' }}>{text}</div>
);

const Tile: React.FC<{ value: string; caption: string; o: number; accent?: boolean; w?: number; size?: number }> =
({ value, caption, o, accent = false, w = 452, size = 132 }) => (
  <div style={{
    width: w, padding: '34px 28px 30px', background: CARD, border: `2px solid ${accent ? ACCENT : HAIR}`,
    opacity: o, transform: `translateY(${(1 - o) * 26}px)`,
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
  }}>
    <div style={{ fontFamily: SERIF, fontSize: size, lineHeight: 1.08, color: accent ? ACCENT : INK, fontWeight: 600 }}>{value}</div>
    <div style={{ fontFamily: SANS, fontSize: 30, letterSpacing: 2.4, textTransform: 'uppercase', color: SOFT, textAlign: 'center', lineHeight: 1.3 }}>{caption}</div>
  </div>
);

const RecordStrip: React.FC<{ text: string; o: number }> = ({ text, o }) => (
  <div style={{
    position: 'absolute', left: SAFE.x, width: SAFE.w, bottom: 118, opacity: o,
    transform: `translateY(${(1 - o) * 18}px)`, display: 'flex', justifyContent: 'center',
  }}>
    <div style={{ borderTop: `3px solid ${ACCENT}`, paddingTop: 20, maxWidth: 1500, fontFamily: SERIF, fontSize: 44, lineHeight: 1.25, color: INK, textAlign: 'center' }}>{text}</div>
  </div>
);

/* B00B — the promise */
export const WfPromise: React.FC<{ spark?: string }> = ({ spark = 'Why watch this.' }) => {
  const p = useP();
  const head = ease(remap(p, 0.04, 0.18, 0, 1));
  const items = [
    { v: 'Lost', c: 'content vanishes silently', hot: true },
    { v: 'Why', c: 'exactly when and why', hot: false },
    { v: 'Fix', c: 'one free setting', hot: false },
  ];
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 118, width: SAFE.w, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26 }}>
        <Eyebrow text="What this video is" o={remap(p, 0, 0.08, 0, 1)} />
        <div style={{ fontFamily: SERIF, fontSize: 88, lineHeight: 1.12, color: INK, textAlign: 'center', maxWidth: 1580, fontWeight: 600, opacity: head, transform: `translateY(${(1 - head) * 30}px)` }}>
          A benchmark for what AI scrapers drop.
        </div>
      </div>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 360, width: SAFE.w, display: 'flex', justifyContent: 'center', gap: 30 }}>
        {items.map((n, i) => (
          <Tile key={n.v} value={n.v} caption={n.c} accent={n.hot} o={ease(remap(p, 0.34 + i * 0.12, 0.50 + i * 0.12, 0, 1))} />
        ))}
      </div>
      <RecordStrip text="No scraping knowledge needed. Every term gets explained." o={remap(p, 0.80, 0.92, 0, 1)} />
    </IlluStage>
  );
};

/* B01 — the snapshot line on a timeline */
export const WfSnapshot: React.FC<{ spark?: string }> = ({ spark = 'The answer first.' }) => {
  const p = useP();
  const W = 1500, x0 = (1920 - W) / 2, t2x = (ms: number) => x0 + (ms / 2000) * W;
  const axis = ease(remap(p, 0.02, 0.12, 0, 1));
  const snap = ease(remap(p, 0.14, 0.28, 0, 1));
  const lost = ease(remap(p, 0.40, 0.56, 0, 1));
  const out = ease(remap(p, 0.62, 0.78, 0, 1));
  const blocks = [
    { at: 0, w: 120, label: 'heading' },
    { at: 150, w: 120, label: 'nav' },
    { at: 800, w: 300, label: 'release notes' },
    { at: 1400, w: 300, label: 'prices' },
  ];
  const axisY = 380;
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: x0, top: 122, width: W, fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: SOFT, textTransform: 'uppercase', opacity: axis }}>
        Page loads → content arrives over time
      </div>
      <div style={{ position: 'absolute', left: x0, top: axisY, width: W * axis, height: 3, background: INK }} />
      {[0, 500, 1000, 1500, 2000].map(ms => (
        <div key={ms} style={{ position: 'absolute', left: t2x(ms) - 60, width: 120, top: axisY + 18, textAlign: 'center', fontFamily: MONO, fontSize: 28, color: SOFT, opacity: axis }}>{ms === 0 ? '0 s' : `${ms / 1000} s`}</div>
      ))}
      {blocks.map((b, i) => {
        const late = b.at > 300;
        const o = ease(remap(p, 0.06 + i * 0.05, 0.16 + i * 0.05, 0, 1));
        return (
          <div key={b.label} style={{
            position: 'absolute', left: t2x(b.at), top: axisY - 120, width: b.w, height: 96,
            background: late ? `rgba(61,57,41,${0.06 + 0.06 * (1 - lost)})` : CARD,
            border: `2px ${late && lost > 0.5 ? 'dashed' : 'solid'} ${HAIR}`, opacity: o,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: SANS, fontSize: 28, color: late ? SOFT : INK,
          }}>
            {late && lost > 0.5 ? <span style={{ color: ACCENT, fontWeight: 700, letterSpacing: 3 }}>LOST</span> : b.label}
          </div>
        );
      })}
      <div style={{ position: 'absolute', left: t2x(300) - 2, top: axisY - 170 + (1 - snap) * -40, width: 4, height: 210 * snap, background: ACCENT }} />
      <div style={{ position: 'absolute', left: t2x(300) + 16, top: axisY - 176, fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: ACCENT, fontWeight: 700, opacity: snap, whiteSpace: 'nowrap' }}>← SNAPSHOT · 0.3 s</div>
      <div style={{
        position: 'absolute', left: (1920 - 980) / 2, top: 560, width: 980, padding: '30px 40px', background: CARD,
        border: `2px solid ${HAIR}`, opacity: out, transform: `translateY(${(1 - out) * 24}px)`,
        fontFamily: MONO, fontSize: 36, lineHeight: 1.5, color: INK,
      }}>
        <div style={{ fontFamily: SANS, fontSize: 24, letterSpacing: 3, color: SOFT, marginBottom: 10 }}>WHAT THE AGENT RECEIVES</div>
        <div># Release Notes</div>
        <div style={{ color: SOFT }}>Loading release notes…</div>
      </div>
      <RecordStrip text="The output looks finished. It isn't." o={remap(p, 0.86, 0.96, 0, 1)} />
    </IlluStage>
  );
};

/* B02 — planted facts */
export const WfPlanted: React.FC<{ spark?: string }> = ({ spark = 'Plant the answers.' }) => {
  const p = useP();
  const page = ease(remap(p, 0.04, 0.16, 0, 1));
  const facts: [string, string, string][] = [
    ['Team plan: ', '$1,284.50', ' per year'],
    ['Model ', 'Velora AB-417', ' ships today'],
    ['Last quarter: ', '233 units', ' sold'],
    ['Includes a ', '38-month warranty', ''],
  ];
  const tiles = [{ v: '36', c: 'test pages' }, { v: '240', c: 'planted facts', hot: true }, { v: '9', c: 'kinds of page' }];
  return (
    <IlluStage spark={spark}>
      <div style={{
        position: 'absolute', left: SAFE.x + 20, top: 150, width: 760, padding: '40px 44px', background: CARD,
        border: `2px solid ${HAIR}`, opacity: page, transform: `translateY(${(1 - page) * 24}px)`,
        fontFamily: SANS, fontSize: 34, lineHeight: 1.9, color: SOFT,
      }}>
        <div style={{ fontFamily: SERIF, fontSize: 46, color: INK, fontWeight: 600, marginBottom: 10 }}>Plans and Pricing</div>
        {facts.map(([pre, f, post], i) => {
          const o = ease(remap(p, 0.14 + i * 0.06, 0.22 + i * 0.06, 0, 1));
          return (
            <div key={f}>{pre}
              <span style={{ background: `rgba(217,119,87,${0.18 * o})`, borderBottom: `3px solid rgba(217,119,87,${o})`, color: INK, padding: '0 6px' }}>{f}</span>{post}
            </div>
          );
        })}
        <div style={{ marginTop: 18, fontFamily: SANS, fontSize: 26, letterSpacing: 2, color: SOFT, textTransform: 'uppercase', opacity: ease(remap(p, 0.36, 0.44, 0, 1)) }}>Highlighted = planted fact</div>
      </div>
      <div style={{ position: 'absolute', left: SAFE.x + 820, top: 190, width: 860, display: 'flex', flexDirection: 'column', gap: 26 }}>
        {tiles.map((t, i) => {
          const o = ease(remap(p, 0.42 + i * 0.09, 0.56 + i * 0.09, 0, 1));
          return (
            <div key={t.c} style={{ display: 'flex', alignItems: 'baseline', gap: 26, opacity: o, transform: `translateX(${(1 - o) * 30}px)` }}>
              <div style={{ fontFamily: SERIF, fontSize: 120, lineHeight: 1, color: t.hot ? ACCENT : INK, fontWeight: 600, width: 260, textAlign: 'right' }}>{t.v}</div>
              <div style={{ fontFamily: SANS, fontSize: 36, letterSpacing: 3, textTransform: 'uppercase', color: SOFT }}>{t.c}</div>
            </div>
          );
        })}
      </div>
      <RecordStrip text="Each fact is either in the output or it isn't. No judgement calls." o={remap(p, 0.82, 0.94, 0, 1)} />
    </IlluStage>
  );
};

/* B03 — the timing curve: share of 5 runs that captured late content */
export const WfTiming: React.FC<{ spark?: string; points?: [number, number][] }> =
({ spark = 'When does it look?', points = [[0, 5], [50, 5], [100, 5], [150, 5], [200, 5], [250, 5], [300, 2], [500, 0], [1000, 0], [2000, 0]] }) => {
  const p = useP();
  const n = points.length, W = 1560, x0 = (1920 - W) / 2, colW = W / n, base = 640, hMax = 380;
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: x0, top: 150, width: W, fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: SOFT, textTransform: 'uppercase', opacity: remap(p, 0, 0.06, 0, 1) }}>
        Content arrives after… · captured in 5 runs
      </div>
      <div style={{ position: 'absolute', left: x0, top: base, width: W, height: 3, background: INK, opacity: remap(p, 0, 0.06, 0, 1) }} />
      {points.map(([ms, hits], i) => {
        const start = ms <= 250 ? 0.06 + i * 0.025 : ms === 300 ? 0.30 : 0.40 + (i - 7) * 0.04;
        const g = ease(remap(p, start, start + 0.10, 0, 1));
        const hot = ms === 300;
        const h = (hits / 5) * hMax * g;
        return (
          <React.Fragment key={ms}>
            {hits > 0 ? (
              <div style={{ position: 'absolute', left: x0 + i * colW + colW * 0.18, width: colW * 0.64, top: base - h, height: h, background: hot ? ACCENT : INK, opacity: hot ? 1 : 0.86 }} />
            ) : (
              <div style={{ position: 'absolute', left: x0 + i * colW + colW * 0.18, width: colW * 0.64, top: base - hMax, height: hMax, border: `2px dashed ${HAIR}`, opacity: g }} />
            )}
            <div style={{ position: 'absolute', left: x0 + i * colW, width: colW, top: base - (hits / 5) * hMax - 52, textAlign: 'center', fontFamily: SERIF, fontSize: 40, fontWeight: 600, color: hot ? ACCENT : INK, opacity: g }}>{hits}/5</div>
            <div style={{ position: 'absolute', left: x0 + i * colW, width: colW, top: base + 16, textAlign: 'center', fontFamily: MONO, fontSize: 26, color: SOFT, opacity: remap(p, 0, 0.06, 0, 1) }}>{ms >= 1000 ? `${ms / 1000}s` : `${ms}ms`}</div>
          </React.Fragment>
        );
      })}
      <RecordStrip text="A slow server call is no different: the browser asks, then snapshots before the answer arrives." o={remap(p, 0.66, 0.80, 0, 1)} />
    </IlluStage>
  );
};

/* B04 — the 100,000-pixel window */
export const WfTallWindow: React.FC<{ spark?: string }> = ({ spark = 'A very tall window.' }) => {
  const p = useP();
  const count = Math.round(100000 * ease(remap(p, 0.10, 0.30, 0, 1)));
  const shown = ease(remap(p, 0.06, 0.16, 0, 1));
  const feed = ease(remap(p, 0.50, 0.66, 0, 1));
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x + 30, top: 160, width: 820, display: 'flex', flexDirection: 'column', gap: 18, opacity: shown }}>
        <div style={{ fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: SOFT, textTransform: 'uppercase' }}>Asked from inside the page</div>
        <div style={{ fontFamily: MONO, fontSize: 44, color: SOFT }}>window.innerHeight</div>
        <div style={{ fontFamily: SERIF, fontSize: 150, lineHeight: 1, color: ACCENT, fontWeight: 600 }}>{count.toLocaleString('en-US')}</div>
        <div style={{ fontFamily: SANS, fontSize: 34, color: INK }}>pixels tall. A laptop screen is about 900.</div>
        <div style={{ fontFamily: MONO, fontSize: 40, color: SOFT, marginTop: 20, opacity: ease(remap(p, 0.34, 0.44, 0, 1)) }}>window.scrollY → still 0</div>
      </div>
      <div style={{ position: 'absolute', left: 1180, top: 150, width: 520, display: 'flex', flexDirection: 'column', gap: 16, opacity: feed }}>
        <div style={{ fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: SOFT, textTransform: 'uppercase' }}>An endless feed</div>
        {['Batch 1', 'Batch 2', 'Batch 3'].map((b, i) => (
          <div key={b} style={{
            height: 150, background: i === 0 ? CARD : 'transparent', border: `2px ${i === 0 ? 'solid' : 'dashed'} ${HAIR}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontSize: 34, color: i === 0 ? INK : SOFT,
          }}>{i === 0 ? b : `${b} · never loads`}</div>
        ))}
      </div>
      <RecordStrip text="Feeds that load as you scroll never load. Scroll commands do nothing." o={remap(p, 0.78, 0.90, 0, 1)} />
    </IlluStage>
  );
};

/* B05 — the fix */
export const WfFix: React.FC<{ spark?: string }> = ({ spark = 'The cheap fix.' }) => {
  const p = useP();
  const a = ease(remap(p, 0.30, 0.44, 0, 1));
  const b = ease(remap(p, 0.44, 0.58, 0, 1));
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 110, width: SAFE.w, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        <Eyebrow text="Wait · scroll · click — before the snapshot" o={remap(p, 0.04, 0.14, 0, 1)} />
      </div>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 230, width: SAFE.w, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 44 }}>
        <Tile value="52%" caption="default settings" o={a} w={560} size={170} />
        <div style={{ fontFamily: SERIF, fontSize: 110, color: SOFT, opacity: b }}>→</div>
        <Tile value="89%" caption="with actions" o={b} w={560} size={170} accent />
      </div>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 600, width: SAFE.w, textAlign: 'center', fontFamily: SANS, fontSize: 32, color: SOFT, opacity: remap(p, 0.58, 0.68, 0, 1) }}>
        Recall = share of planted facts that came through · 36 test pages
      </div>
      <RecordStrip text="Same price either way: one credit per page." o={remap(p, 0.82, 0.94, 0, 1)} />
    </IlluStage>
  );
};

/* B06 — the real web */
export const WfRealWeb: React.FC<{ spark?: string; value?: string; caption?: string }> =
({ spark = 'On the real web.', value = '85%', caption = 'captured by default · 46 held-out real sites' }) => {
  const p = useP();
  const big = ease(remap(p, 0.30, 0.46, 0, 1));
  const rows = [
    { k: 'Page that renders after 2 s', v: '0% → 100% with a wait' },
    { k: 'Endless scroll feed', v: '9% → 9% with scrolling' },
  ];
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x + 40, top: 200, width: 640 }}>
        <Tile value={value} caption={caption} o={big} w={600} size={190} accent />
      </div>
      <div style={{ position: 'absolute', left: 820, top: 220, width: 900, display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div style={{ fontFamily: SANS, fontSize: 30, letterSpacing: 3, color: SOFT, textTransform: 'uppercase', opacity: remap(p, 0.56, 0.64, 0, 1) }}>Both failures, on real sites</div>
        {rows.map((r, i) => {
          const o = ease(remap(p, 0.62 + i * 0.1, 0.74 + i * 0.1, 0, 1));
          return (
            <div key={r.k} style={{ background: CARD, border: `2px solid ${HAIR}`, padding: '24px 32px', opacity: o, transform: `translateY(${(1 - o) * 20}px)` }}>
              <div style={{ fontFamily: SANS, fontSize: 30, color: SOFT }}>{r.k}</div>
              <div style={{ fontFamily: SERIF, fontSize: 54, color: INK, fontWeight: 600 }}>{r.v}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: 'absolute', left: SAFE.x, width: SAFE.w, bottom: 70, textAlign: 'center', fontFamily: SANS, fontSize: 26, letterSpacing: 2, color: SOFT, opacity: remap(p, 0.2, 0.3, 0, 1) }}>
        MEASURED OCTOBER 2026 · ANSWER KEY = A PATIENT BROWSER, LOADED BEFORE AND AFTER EACH SCRAPE
      </div>
    </IlluStage>
  );
};

/* B06B — the honest failure */
export const WfHonest: React.FC<{ spark?: string; testValue?: string; realValue?: string }> =
({ spark = 'What didn’t hold.', testValue = '90%', realValue = '1 of 3' }) => {
  const p = useP();
  const a = ease(remap(p, 0.22, 0.36, 0, 1));
  const b = ease(remap(p, 0.44, 0.58, 0, 1));
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 110, width: SAFE.w, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Eyebrow text="A detector for incomplete scrapes" o={remap(p, 0.04, 0.14, 0, 1)} />
      </div>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 230, width: SAFE.w, display: 'flex', justifyContent: 'center', gap: 60 }}>
        <Tile value={testValue} caption="right, on my own test pages" o={a} w={600} size={170} />
        <Tile value={realValue} caption="caught, on unseen real sites" o={b} w={600} size={170} accent />
      </div>
      <RecordStrip text="Rules tuned on your own pages fool you. Check on data the rules never saw." o={remap(p, 0.76, 0.90, 0, 1)} />
    </IlluStage>
  );
};

/* B07 — the verdict */
export const WfVerdict: React.FC<{ spark?: string }> = ({ spark = 'What to do.' }) => {
  const p = useP();
  const rows = [
    { q: 'Page loads data after it opens?', a: 'Add a wait before the snapshot.' },
    { q: 'An endless feed?', a: 'Scrolling won’t help. Fetch its pages directly.' },
    { q: 'Measuring anything?', a: 'Keep a test set you never tune on.' },
  ];
  return (
    <IlluStage spark={spark}>
      <div style={{ position: 'absolute', left: SAFE.x, top: SAFE.y + 66, width: SAFE.w, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        {rows.map((r, i) => {
          const t = ease(remap(p, 0.06 + i * 0.2, 0.26 + i * 0.2, 0, 1));
          return (
            <div key={r.q} style={{
              width: SAFE.w - 140, padding: '22px 44px', background: CARD, border: `2px solid ${i === 2 ? ACCENT : HAIR}`,
              opacity: t, transform: `translateY(${(1 - t) * 24}px)`, display: 'flex', flexDirection: 'column', gap: 6,
            }}>
              <div style={{ fontFamily: SERIF, fontSize: 54, color: INK, fontWeight: 600 }}>{r.q}</div>
              <div style={{ fontFamily: SANS, fontSize: 36, color: SOFT }}>{r.a}</div>
            </div>
          );
        })}
      </div>
      <RecordStrip text="The settings will change. The habit of checking won’t." o={remap(p, 0.80, 0.92, 0, 1)} />
    </IlluStage>
  );
};

/* B09 — the outro */
export const WfOutro: React.FC<{ title?: string; handle?: string; subline?: string }> =
({ title = 'Half a Page.', handle = 'Param Madan', subline = 'WebFidelity' }) => {
  const p = useP();
  const rise = ease(remap(p, 0.02, 0.30, 0, 1));
  const nameO = remap(p, 0.24, 0.48, 0, 1);
  const subO = remap(p, 0.44, 0.66, 0, 1);
  const hasDot = title.trim().endsWith('.');
  const stem = hasDot ? title.trim().slice(0, -1) : title.trim();
  return (
    <AbsoluteFill style={{ background: CLAUDE.PAGE, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 30 }}>
      <div style={{ fontFamily: SERIF, fontSize: 196, lineHeight: 1.02, fontWeight: 600, color: INK, maxWidth: SAFE.w, textAlign: 'center', opacity: rise, transform: `translateY(${(1 - rise) * 40}px)` }}>
        {stem}{hasDot && <span style={{ color: ACCENT }}>.</span>}
      </div>
      <div style={{ fontFamily: SERIF, fontSize: 86, color: INK, opacity: nameO, transform: `translateY(${(1 - ease(nameO)) * 22}px)` }}>{handle}</div>
      <div style={{ fontFamily: SANS, fontSize: 40, letterSpacing: 5, textTransform: 'uppercase', color: SOFT, opacity: subO }}>{subline}</div>
    </AbsoluteFill>
  );
};
