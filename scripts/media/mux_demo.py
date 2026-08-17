#!/usr/bin/env python3
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "demo-video"
VIDEO = OUT / "browser-capture.webm"
AUDIO = OUT / "voiceover.mp3"
FINAL = OUT / "prizepilot-demo.mp4"

if not VIDEO.exists():
    raise SystemExit(f"Missing {VIDEO}")
if not AUDIO.exists():
    raise SystemExit(f"Missing {AUDIO}")

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

def duration(path: Path) -> float:
    probe = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    for line in probe.stderr.splitlines():
        if "Duration:" not in line:
            continue
        timestamp = line.split("Duration:", 1)[1].split(",", 1)[0].strip()
        hours, minutes, seconds = timestamp.split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise RuntimeError(f"Could not determine duration for {path}")

audio_duration = duration(AUDIO)
video_duration = duration(VIDEO)

pad_seconds = max(0, audio_duration - video_duration + 0.25)
filter_complex = (
    "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#111820,"
    f"setsar=1,fps=30,tpad=stop_mode=clone:stop_duration={pad_seconds:.3f}[v]"
)

cmd = [
    ffmpeg,
    "-y",
    "-i",
    str(VIDEO),
    "-i",
    str(AUDIO),
    "-filter_complex",
    filter_complex,
    "-map",
    "[v]",
    "-map",
    "1:a",
    "-t",
    f"{audio_duration:.3f}",
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "20",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    "-b:a",
    "192k",
    "-movflags",
    "+faststart",
    str(FINAL),
]
subprocess.run(cmd, check=True)
print(f"video_seconds={video_duration:.2f}")
print(f"audio_seconds={audio_duration:.2f}")
print(FINAL)
