import os, subprocess, tempfile, glob
import imageio_ffmpeg
from llm import client

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
MAX_BYTES = 24 * 1024 * 1024
PART_SECONDS = 600

def _compress(src, dst):
    subprocess.run([FFMPEG, "-y", "-i", src, "-ac", "1", "-ar", "16000", "-b:a", "32k", dst],
                   check=True, capture_output=True)

def _split(src, outdir):
    pattern = os.path.join(outdir, "part_%03d.mp3")
    subprocess.run([FFMPEG, "-y", "-i", src, "-f", "segment", "-segment_time", str(PART_SECONDS),
                    "-c", "copy", pattern], check=True, capture_output=True)
    return sorted(glob.glob(os.path.join(outdir, "part_*.mp3")))

def _ts(sec):
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"

def transcribe(path):
    tmp = tempfile.mkdtemp()
    small = os.path.join(tmp, "audio.mp3")
    _compress(path, small)
    files = [small] if os.path.getsize(small) <= MAX_BYTES else _split(small, tmp)

    lines, offset = [], 0
    for f in files:
        with open(f, "rb") as fh:
            r = client.audio.transcriptions.create(
                file=(os.path.basename(f), fh.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
            )
        segs = getattr(r, "segments", None)
        if segs:
            for s in segs:
                lines.append(f"[{_ts(offset + s['start'])}] {s['text'].strip()}")
        else:
            lines.append(r.text)           # fallback if segments aren't returned
        offset += PART_SECONDS
    return "\n".join(lines)
