import argparse, sys
from . import __version__
from .storyboard import load, lint, StoryboardError
from .subtitles import to_srt
from .render import render, RenderError


def main(argv=None):
    p = argparse.ArgumentParser(prog="canhreel", description="Dựng video từ storyboard JSON")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, h in [("plan", "In timeline đã tự tính thời lượng"), ("lint", "Kiểm tra storyboard"),
                    ("srt", "Xuất phụ đề .srt"), ("render", "Dựng video MP4")]:
        sp = sub.add_parser(name, help=h); sp.add_argument("storyboard")
        if name in ("srt", "render"):
            sp.add_argument("-o", "--output", required=name == "render")
        if name == "render":
            sp.add_argument("--no-subs", action="store_true", help="Không đốt phụ đề vào video")
    a = p.parse_args(argv)
    try:
        sb = load(a.storyboard)
        if a.cmd == "plan":
            print(f"{sb.title}: {len(sb.scenes)} cảnh, {sb.total:.2f}s @ {sb.wpm} wpm")
            for i, s in enumerate(sb.scenes, 1):
                print(f"{i:>3}  {s.start:7.2f}s  {s.duration:5.2f}s  {s.text[:50]}")
        elif a.cmd == "lint":
            w = lint(sb)
            print("\n".join(w) if w else "OK: không có cảnh báo")
            return 1 if w else 0
        elif a.cmd == "srt":
            data = to_srt(sb)
            if a.output:
                open(a.output, "w", encoding="utf-8").write(data)
            else:
                sys.stdout.write(data)
        else:
            for w in lint(sb):
                print("cảnh báo:", w, file=sys.stderr)
            print("Đã xuất:", render(sb, a.output, burn_subs=not a.no_subs))
    except (StoryboardError, RenderError, OSError) as e:
        print("Lỗi:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
