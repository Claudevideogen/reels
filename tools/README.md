# Reel tools (split-screen 9:16 reels)

Pipeline used for @itsavacollins1 reels. See the "saim" project playbook for script rules.

Setup in a fresh workspace:
```
pip install --break-system-packages kokoro-onnx soundfile scipy
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```
(gen.py expects the model files at /home/claude/reel/tts/ — adjust paths.)

Steps: `python3 gen.py` (voices + timing.json) → `python3 audio.py` (mix.wav) → `python3 render.py video 0 N out.mp4` (render in parts, concat, add mix.wav with ffmpeg).

Modules: people*.py = characters, plinko/breakout/snake/tower.py = bottom games (rotate each video).
Pixabay key: read from env var PIXABAY_API_KEY (never commit keys).
