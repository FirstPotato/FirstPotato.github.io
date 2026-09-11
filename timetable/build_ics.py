"""Build timetable.ics from timetable.json. Used locally and by GitHub Actions."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def ics_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def write_ics(data: dict, dest: Path) -> None:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//autumn-timetable//CN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:2026秋季课表",
        "X-WR-TIMEZONE:Asia/Shanghai",
    ]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for i, session in enumerate(data["sessions"], 1):
        day = session["date"].replace("-", "")
        nxt = (datetime.strptime(session["date"], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d")
        summary = f"{session['shortName']} {session['period']}"
        desc = ics_escape(session["course"])
        if session.get("note"):
            desc += "\\n" + ics_escape(session["note"])
        lines += [
            "BEGIN:VEVENT",
            f"UID:timetable-{session['date']}-{i}@local",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{day}",
            f"DTEND;VALUE=DATE:{nxt}",
            f"SUMMARY:{ics_escape(summary)}",
            f"LOCATION:{ics_escape(session.get('location') or '')}",
            f"DESCRIPTION:{desc}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes("\r\n".join(lines).encode("utf-8"))


def resolve_io() -> tuple[Path, list[Path]]:
    here = Path(__file__).resolve().parent
    if (here / "timetable.json").exists():
        return here / "timetable.json", [here / "timetable.ics"]
    root = here.parent
    dests = [root / "web" / "timetable.ics", root / "dist" / "秋季课表.ics"]
    return root / "data" / "timetable.json", dests


def main() -> None:
    src, dests = resolve_io()
    data = json.loads(src.read_text(encoding="utf-8"))
    for dest in dests:
        write_ics(data, dest)
        print(f"wrote {dest} sessions={len(data['sessions'])}")


if __name__ == "__main__":
    main()
