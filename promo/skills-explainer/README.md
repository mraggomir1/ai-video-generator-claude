# Skills explainer video

Vertical (1080×1920) ~47s Russian explainer about the 10 skills in this repo.

Pipeline:
1. `python3 build_audio.py` — edge-tts voiceover per scene + word timings → `voice.wav`, `scenes.json`
2. `node render.js full` — Playwright renders `page.html` frame by frame → `frames/`
3. ffmpeg mixes voice + ambient pad + whooshes and encodes `skills-explainer.mp4`
