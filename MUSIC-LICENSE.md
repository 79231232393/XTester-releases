# Replacement music — exact recording and commercial-use evidence

- Title: **Signal to Noise**
- Composer / recording source: **Scott Buckley**.
- Canonical track page: https://www.scottbuckley.com.au/library/signal-to-noise/
- Exact downloaded full mix: https://www.scottbuckley.com.au/library/wp-content/uploads/2020/04/sb_signaltonoise.mp3
- Local original: `composition/assets/sb_signaltonoise.mp3` (353.498889 seconds).
- License: **Creative Commons Attribution 4.0 International**, https://creativecommons.org/licenses/by/4.0/
- Exact track page explicitly states: “free for use in any project (including commercial) as long as I'm credited.” Commercial advertising is permitted subject to attribution; this is NOT CC0 or a no-attribution license.
- Saved evidence: `music-signal-to-noise.html`, `music-cc-by-4.0.html`.
- No subscription, purchase or account created. Other downloaded HTML pages were research alternatives, not soundtrack sources.

## Required attribution (retain with any external publication)

“Signal to Noise” by Scott Buckley — released under CC BY 4.0.
https://www.scottbuckley.com.au/library/signal-to-noise/
https://creativecommons.org/licenses/by/4.0/
www.scottbuckley.com.au
Edited: 32–61 second excerpt, fades, loudness normalization and mix level.

A compact music credit is included in the final endcard. Retain this full attribution in an accompanying description / website credits. The artist specifically requires YouTube description credit, even if video credit exists. Do not remove the credit or claim attribution-free clearance. No external publication was performed.

## Musical treatment and reproducibility

Real existing produced recording: piano, solo cello, warm synths, low strings; serious restrained cinematic/electronic texture rather than the rejected procedural console-like loop. This is a softer cinematic-electronic interpretation, not a hard dance beat. No audible-listening acceptance is claimed by the renderer; parent/owner should assess the musical fit in actual playback.

29-second edit: source 32–61 seconds at original speed. Fade in 0.45 s; 2.4 s resolve-out from 26.6 s; normalize source edit to -19 LUFS / -2 dBTP, then existing music-only assembler gain 0.8 and limiter. No generated beeps or repeated loop. Future narration uses existing lower gain and sidechain ducking.

Rebuild `composition/assets/score.wav`:
```
ffmpeg -v warning -y -ss 32 -i composition/assets/sb_signaltonoise.mp3 -t 29 -af 'afade=t=in:d=0.45,afade=t=out:st=26.6:d=2.4,loudnorm=I=-19:TP=-2:LRA=7' -ar 48000 -ac 2 composition/assets/score.wav
```
The old original procedural WAV is preserved in `backup-before-music-endcard/composition/assets/score.wav`.
