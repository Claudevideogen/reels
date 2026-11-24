#!/bin/bash
# One-time setup in a fresh session: python deps + Kokoro TTS model (from GitHub releases; HF is blocked).
set -e
pip install -q --break-system-packages kokoro-onnx soundfile scipy numpy pillow >/dev/null 2>&1 || true
mkdir -p ~/tts && cd ~/tts
[ -f kokoro-v1.0.int8.onnx ] || curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f voices-v1.0.bin ] || curl -sSLO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
ls -la ~/tts; which ffmpeg; fc-list | grep -c Poppins
