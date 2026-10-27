"""Dựng video: mỗi cảnh thành 1 clip, rồi nối bằng concat demuxer."""
import os, shutil, subprocess, tempfile
from .subtitles import to_srt


class RenderError(RuntimeError):
    pass


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RenderError("FFmpeg lỗi:\n" + p.stderr[-800:])


def scene_cmd(sb, s, out):
    w, h = sb.width, sb.height
    img = os.path.join(sb.base_dir, s.image) if s.image else ""
    if img and os.path.exists(img):
        src = ["-loop", "1", "-i", img]
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    else:
        src = ["-f", "lavfi", "-i", f"color=c={s.color}:s={w}x{h}:r={sb.fps}"]
        vf = "setsar=1"
    return ["ffmpeg", "-y", "-loglevel", "error", *src, "-t", str(s.duration),
            "-vf", vf + f",fps={sb.fps},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", out]


def render(sb, out, burn_subs=True):
    if not shutil.which("ffmpeg"):
        raise RenderError("Không tìm thấy ffmpeg trong PATH")
    out = os.path.abspath(out)
    with tempfile.TemporaryDirectory() as tmp:
        clips = []
        for i, s in enumerate(sb.scenes):
            c = os.path.join(tmp, f"s{i:03}.mp4")
            _run(scene_cmd(sb, s, c)); clips.append(c)
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{c}'\n" for c in clips)
        srt = os.path.join(tmp, "subs.srt")
        with open(srt, "w", encoding="utf-8") as f:
            f.write(to_srt(sb))
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst]
        audio = os.path.join(sb.base_dir, sb.audio) if sb.audio else ""
        if audio and os.path.exists(audio):
            cmd += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-shortest"]
        if burn_subs and os.path.getsize(srt):
            cmd += ["-vf", f"subtitles={srt}", "-c:v", "libx264", "-preset", "veryfast"]
        else:
            cmd += ["-c:v", "copy"]
        _run(cmd + [out])
    return out
