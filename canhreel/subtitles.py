def _ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def to_srt(sb):
    out, n = [], 0
    for s in sb.scenes:
        if not s.text.strip():
            continue
        n += 1
        out.append(f"{n}\n{_ts(s.start)} --> {_ts(s.start + s.duration)}\n{s.text.strip()}\n")
    return "\n".join(out)
