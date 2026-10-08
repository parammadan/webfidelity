# BUILD-LOG — half-a-page

2026-10-08 · built by Claude for Param Madan (personal project: no Humanitarians PR).

1. **Numbers firmed before audio.** The video waited for a second held-out set of real sites. B06
   moved from "89% on 25 sites" to "85% on 46 sites", and B06B from "1 of 3" to "2 of 9". The
   more conservative numbers went in.
2. **Speech QC (Whisper).** "your A I agent" was heard as "iAgent". B00 rephrased to "an A I agent";
   only B00 regenerated. Whisper writes the host name "Madden"; it is spoken correctly.
3. **Frame QC caught two defects at p≈0.92:**
   - B01: the "SNAPSHOT · 0.3 s" label overlapped the header. Header moved up; label moved beside the line.
   - B02: the fact card read "The plan costs Velora AB-417 / 233 units…" (one template sentence for
     every fact). Replaced with one real sentence per fact plus a "highlighted = planted fact" key.
   - B04: a code line wrapped mid-phrase; shortened to "window.scrollY → still 0".
4. **Interrupted render.** The session ended mid-render and left a 48-byte B05.mp4. B05–B09 were
   re-rendered with `--force`; the size of every media file was checked before compiling.
5. **Lint notes accepted:** OUTRO LAW (WfOutro carries the host name, same deviation as earlier reels);
   motion histogram 9/12 "illustrate" (over the ~40% guideline). Logged, not fixed.
6. Master verified: 3840×2160 h264 + aac, 227.2 s.
