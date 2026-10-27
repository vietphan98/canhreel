"""Đọc, kiểm tra và tính thời lượng storyboard."""
import json, os
from dataclasses import dataclass, field

DEFAULT_WPM = 150      # tốc độ đọc mặc định (từ/phút)
MIN_SCENE = 1.5        # giây tối thiểu mỗi cảnh
PAD = 0.6              # giây nghỉ thêm sau lời đọc


class StoryboardError(ValueError):
    pass


@dataclass
class Scene:
    text: str = ""
    image: str = ""
    color: str = "black"
    duration: float = 0.0     # 0 = tự tính từ lời đọc
    start: float = 0.0


@dataclass
class Storyboard:
    title: str
    width: int
    height: int
    fps: int
    wpm: int
    scenes: list = field(default_factory=list)
    audio: str = ""
    base_dir: str = "."

    @property
    def total(self):
        return sum(s.duration for s in self.scenes)


def auto_duration(text, wpm):
    words = len(text.split())
    return max(MIN_SCENE, round(words / wpm * 60 + PAD, 2)) if words else MIN_SCENE


def parse(data, base_dir="."):
    if not isinstance(data, dict):
        raise StoryboardError("Storyboard phải là một object JSON")
    raw = data.get("scenes")
    if not isinstance(raw, list) or not raw:
        raise StoryboardError("Cần ít nhất một cảnh trong 'scenes'")
    wpm = int(data.get("wpm", DEFAULT_WPM))
    if wpm <= 0:
        raise StoryboardError("'wpm' phải > 0")
    sb = Storyboard(title=str(data.get("title", "untitled")),
                    width=int(data.get("width", 1280)), height=int(data.get("height", 720)),
                    fps=int(data.get("fps", 25)), wpm=wpm,
                    audio=data.get("audio", ""), base_dir=base_dir)
    t = 0.0
    for i, r in enumerate(raw, 1):
        if not isinstance(r, dict):
            raise StoryboardError(f"Cảnh {i}: phải là object")
        s = Scene(text=str(r.get("text", "")), image=r.get("image", ""),
                  color=r.get("color", "black"), duration=float(r.get("duration", 0)))
        if s.duration < 0:
            raise StoryboardError(f"Cảnh {i}: duration âm")
        if s.duration == 0:
            s.duration = auto_duration(s.text, wpm)
        s.start = round(t, 3)
        t += s.duration
        sb.scenes.append(s)
    return sb


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StoryboardError(f"JSON lỗi dòng {e.lineno}: {e.msg}")
    return parse(data, os.path.dirname(os.path.abspath(path)))


def lint(sb):
    """Trả về danh sách cảnh báo (không chặn render)."""
    warns = []
    for i, s in enumerate(sb.scenes, 1):
        if s.image and not os.path.exists(os.path.join(sb.base_dir, s.image)):
            warns.append(f"Cảnh {i}: không thấy ảnh '{s.image}', sẽ dùng nền màu")
        need = auto_duration(s.text, sb.wpm)
        if s.text and s.duration < need - PAD:
            warns.append(f"Cảnh {i}: {s.duration}s có thể quá ngắn để đọc hết (~{need}s)")
        if len(s.text) > 140:
            warns.append(f"Cảnh {i}: chữ dài {len(s.text)} ký tự, nên tách cảnh")
    if sb.audio and not os.path.exists(os.path.join(sb.base_dir, sb.audio)):
        warns.append(f"Không thấy file audio '{sb.audio}'")
    return warns
