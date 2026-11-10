"""One statistic's hours as the Recorder gives them, kept compact (audit of 9 Nov. 2026, lot 2).

A year of 71 statistics is about 540 000 hours. Kept as one small dictionary each, with its own date, it held 180 MB;
here each statistic is a few columns of numbers side by side (the hour's start in seconds, then the sum, mean, min, max
when the statistic has them), about 15 MB for the same year. Nothing else changes: `Rows` still reads as a list of
{start, mean, min, max, sum} (None where the Recorder has nothing), so every reader of rows works unchanged; the busy
ones read the columns directly.
"""
from __future__ import annotations

from array import array
from bisect import bisect_left
from collections.abc import Iterable, Iterator, Sequence
from datetime import UTC, datetime

FIELDS = ("mean", "min", "max", "sum")
NAN = float("nan")
_TIMES: dict[float, datetime] = {}


def when(stamp: float) -> datetime:
    """The hour's start as an aware datetime (UTC), one shared object per hour: 71 statistics share the same hours."""
    found = _TIMES.get(stamp)
    if found is None:
        if len(_TIMES) > 100_000:
            _TIMES.clear()
        found = _TIMES[stamp] = datetime.fromtimestamp(stamp, UTC)
    return found


class Rows(Sequence):
    """The hours of one statistic, in order. `ts`: each hour's start (UTC seconds); `cols`: the columns that hold a
    value somewhere ({« sum »: array…}), NaN where that hour has none."""
    __slots__ = ("ts", "cols")

    def __init__(self, ts: array | None = None, cols: dict[str, array] | None = None) -> None:
        self.ts = ts if ts is not None else array("d")
        self.cols = cols or {}

    @classmethod
    def of(cls, rows: Iterable) -> Rows:
        """From rows as dictionaries ({start: datetime or seconds, mean, min, max, sum}), the Recorder's or a test's."""
        if isinstance(rows, Rows):
            return rows
        rows = rows if isinstance(rows, list) else list(rows)
        if not rows:
            return cls()
        starts = [row["start"] for row in rows]
        ts = array("d", [s.timestamp() for s in starts] if isinstance(starts[0], datetime) else starts)
        cols = {}
        for f in FIELDS:
            values = [row.get(f) for row in rows]
            if any(v is not None for v in values):
                cols[f] = array("d", [NAN if v is None else v for v in values])
        return cls(ts, cols)

    # --- read as a list of dictionaries -------------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.ts)

    def _row(self, i: int) -> dict:
        out = {"start": when(self.ts[i])}
        for f in FIELDS:
            col = self.cols.get(f)
            v = col[i] if col is not None else NAN
            out[f] = None if v != v else v
        return out

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Rows(self.ts[index], {f: c[index] for f, c in self.cols.items()})
        if index < 0:
            index += len(self.ts)
        if not 0 <= index < len(self.ts):
            raise IndexError(index)
        return self._row(index)

    def __iter__(self) -> Iterator[dict]:
        for i in range(len(self.ts)):
            yield self._row(i)

    def __reversed__(self) -> Iterator[dict]:
        for i in range(len(self.ts) - 1, -1, -1):
            yield self._row(i)

    def __eq__(self, other) -> bool:
        """The same hours and the same values (NaN equal to NaN: compared as stored)."""
        if not isinstance(other, Rows):
            return NotImplemented
        return (self.ts.tobytes() == other.ts.tobytes() and set(self.cols) == set(other.cols)
                and all(c.tobytes() == other.cols[f].tobytes() for f, c in self.cols.items()))

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        return f"Rows({len(self)} heures, {', '.join(self.cols)})"

    # --- the columns ------------------------------------------------------------------------------------------------

    def column(self, name: str) -> array | None:
        return self.cols.get(name)

    def before(self, start: datetime) -> Rows:
        """The hours that start before `start`."""
        return self[:bisect_left(self.ts, start.timestamp())]

    def __add__(self, other: Rows) -> Rows:
        other = Rows.of(other)
        n, m = len(self), len(other)
        cols = {}
        for f in set(self.cols) | set(other.cols):
            mine = self.cols.get(f, array("d", [NAN]) * n)
            theirs = other.cols.get(f, array("d", [NAN]) * m)
            cols[f] = mine + theirs
        return Rows(self.ts + other.ts, {f: cols[f] for f in FIELDS if f in cols})


def merge(old: Rows | None, fresh: Rows | None, start: datetime) -> Rows:
    """The hours kept before `start`, then those read again from `start`."""
    old, fresh = Rows.of(old or []), Rows.of(fresh or [])
    return old.before(start) + fresh
