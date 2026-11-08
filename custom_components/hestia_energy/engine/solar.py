"""The panels' health (5.5, palier 3): a panel that falls behind its usual share, an inverter that stops answering.

Each panel (an inverter's channel) keeps about the same share of the day's sun from one day to the next: shade and
the season move it slowly. A panel whose share falls under half of its usual one, on a day that produced enough to
judge, is behind (soiled, shaded by something new, a failing panel or connector). On Frank's real year (10 channels
of OpenDTU), no day crosses that line; winter shade brings some to 52-60 %, which is why the line is at half.
"""
from __future__ import annotations

from collections import defaultdict
import re
from dataclasses import dataclass
from datetime import date, datetime, tzinfo
import statistics

SHARE = 0.5          # under half of its usual share
MIN_DAY_KWH = 3.0    # of a day that produced at least this much
WINDOW = 21          # the usual share: the median of the days before, at most three weeks
MIN_DAYS = 7         # with at least a week of them


def channel_days(rows: dict[str, list[dict]], tz: tzinfo) -> dict[date, dict[str, float]]:
    """Each day's energy of each channel (kWh) from its hourly mean power (W); a day counts only with every channel."""
    out: dict[date, dict[str, float]] = defaultdict(dict)
    for channel, values in rows.items():
        for row in values:
            if row.get("mean") is None:
                continue
            day = row["start"].astimezone(tz).date()
            out[day][channel] = out[day].get(channel, 0.0) + max(0.0, row["mean"]) / 1000
    return {d: v for d, v in out.items() if len(v) == len(rows)}


@dataclass(frozen=True)
class Behind:
    channel: str
    ratio: float      # its share that day against its usual share (0.3: 70 % less than usual)
    kwh: float


def behind(days: dict[date, dict[str, float]], day: date) -> list[Behind]:
    """The panels behind on `day`. Nothing to say without enough sun that day or enough days before."""
    if day not in days:
        return []
    total = sum(days[day].values())
    if total < MIN_DAY_KWH:
        return []
    before = [d for d in sorted(days) if d < day and sum(days[d].values()) >= MIN_DAY_KWH][-WINDOW:]
    if len(before) < MIN_DAYS:
        return []
    out = []
    for channel, kwh in days[day].items():
        usual = statistics.median(days[d][channel] / sum(days[d].values()) for d in before)
        if usual <= 0.03:
            continue
        ratio = (kwh / total) / usual
        if ratio < SHARE:
            out.append(Behind(channel, ratio, kwh))
    return sorted(out, key=lambda b: b.ratio)


def silent_minutes(state: str | None, changed: datetime | None, now: datetime, sun_up: bool) -> float | None:
    """How long the inverter has not answered while the sun is up (minutes), None when it answers or at night."""
    if not sun_up or changed is None or state not in ("unavailable", "unknown", None):
        return None
    return max(0.0, (now - changed).total_seconds() / 60)


def panel_name(name: str) -> str:
    """« SUD-2 CH1 Power » → « Sud-2 · voie 1 »: the household's own name of the panel, without the inverter's words."""
    text = re.sub(r"\s*(power|puissance)$", "", name.strip(), flags=re.I)
    text = re.sub(r"\s*ch\s*(\d+)$", r" · voie \1", text, flags=re.I)
    head, sep, tail = text.partition(" · ")
    return head[:1].upper() + head[1:].lower() + sep + tail
