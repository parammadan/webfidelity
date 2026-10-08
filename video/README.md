# Half a Page. — Brutalist rebuild guide

**Topic:** what AI scrapers silently drop (WebFidelity × Firecrawl) · **Host:** Param Madan ·
**Voice:** Kokoro `af_bella` · **Palette:** claude · **Length:** 3:47, 12 beats · **Cost:** $0.00

## Files
- `beat_sheet.json`: the beats (narration in `narration_text`, scene props in `shot.remotion.props`)
- `src/WebFidelity.tsx`: the 10 custom scenes; `src/Root.registration.tsx`: the exact Root.tsx lines
- `mp3/`: narration (ground-truth clock) · `SOURCES.md`: every figure → its result file
- `PEDAGOGY.md`: GATE P, signed · `BUILD-LOG.md`: what broke and why · `description.txt`: chapters + prompt

## Rebuild
```bash
cd ~/brutalist.art
cp <this>/src/WebFidelity.tsx runtime/remotion/src/scenes/   # and add Root.registration.tsx lines to Root.tsx
./.venv/bin/python runtime/scripts/generate_audio_kokoro.py <reel>
./.venv/bin/python runtime/scripts/remotion_scenes.py <reel>
./art final <reel>
```
Figures come from `~/webfidelity` results (repo parammadan/webfidelity). If Firecrawl's renderer
changes, re-run the probes there and update the props, not the scene code.
