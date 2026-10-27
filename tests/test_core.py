import json, os, shutil, subprocess, pytest
from canhreel.storyboard import parse, auto_duration, lint, StoryboardError, MIN_SCENE
from canhreel.subtitles import to_srt, _ts
from canhreel.render import render
from canhreel.cli import main

EX = os.path.join(os.path.dirname(__file__), "..", "examples", "demo.json")

def test_auto_duration():
    assert auto_duration("", 150) == MIN_SCENE
    assert auto_duration(" ".join(["a"] * 150), 150) == 60.6

def test_parse_timeline():
    sb = parse({"scenes": [{"text": "a b", "duration": 2}, {"duration": 3}]})
    assert [s.start for s in sb.scenes] == [0, 2] and sb.total == 5

@pytest.mark.parametrize("bad", [{}, {"scenes": []}, {"scenes": [{"duration": -1}]}, {"wpm": 0, "scenes": [{}]}])
def test_parse_errors(bad):
    with pytest.raises(StoryboardError):
        parse(bad)

def test_srt():
    assert _ts(3661.5) == "01:01:01,500"
    srt = to_srt(parse({"scenes": [{"text": "xin chào", "duration": 2}, {"duration": 1}]}))
    assert srt.startswith("1\n00:00:00,000 --> 00:00:02,000\nxin chào")

def test_lint_warns():
    sb = parse({"scenes": [{"text": " ".join(["từ"] * 40), "duration": 2, "image": "nope.png"}]})
    w = lint(sb)
    assert any("ảnh" in x for x in w) and any("ngắn" in x for x in w)

def test_cli_plan(capsys):
    assert main(["plan", EX]) == 0
    assert "3 cảnh" in capsys.readouterr().out

@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="cần ffmpeg")
def test_render(tmp_path):
    sb = parse(json.load(open(EX)), os.path.dirname(EX))
    out = render(sb, str(tmp_path / "o.mp4"))
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                         capture_output=True, text=True).stdout
    assert abs(float(dur) - sb.total) < 0.3
