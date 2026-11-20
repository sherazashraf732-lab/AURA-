"""Data Studio (M07): CSV/XLSX import, schema inference, cleaning, statistics, chart data, export.

Standard library + openpyxl only (no pandas), with hard size limits so analysis stays light on the
8 GB dev machine and on free hosting.
"""

import csv
import io
import statistics
from collections import Counter, defaultdict
from collections.abc import Callable
from typing import Literal

from app.core.errors import AppError

MAX_ROWS = 50_000
MAX_COLS = 100
MAX_CELL = 1000

Agg = Literal["sum", "mean", "count", "min", "max"]


def _num(v: str) -> float | None:
    try:
        return float(v.replace(",", "")) if v.strip() else None
    except ValueError:
        return None


def parse_table(filename: str, data: bytes) -> tuple[list[str], list[list[str]]]:
    name = filename.lower()
    try:
        if name.endswith(".csv"):
            if b"\x00" in data[:4096]:
                raise AppError("invalid_file", "This does not look like a CSV file.", 415)
            reader = csv.reader(io.StringIO(data.decode("utf-8-sig", "replace")))
            rows = [r for _, r in zip(range(MAX_ROWS + 1), reader, strict=False)]
        elif name.endswith(".xlsx"):
            if not data.startswith(b"PK\x03\x04"):
                raise AppError("invalid_file", "This file is not a valid Excel workbook.", 415)
            from openpyxl import load_workbook

            wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
            ws = wb.worksheets[0]
            rows = [
                ["" if v is None else str(v) for v in r]
                for _, r in zip(range(MAX_ROWS + 1), ws.iter_rows(values_only=True), strict=False)
            ]
            wb.close()
        else:
            raise AppError("unsupported_file", "Upload a .csv or .xlsx file.", 415)
    except AppError:
        raise
    except Exception as e:
        raise AppError("unreadable_file", "AURA could not read this table.", 422) from e
    if not rows or not any(rows[0]):
        raise AppError("no_data", "The table is empty.", 422)
    if len(rows) > MAX_ROWS:
        raise AppError("too_large", f"Tables are limited to {MAX_ROWS:,} rows.", 413)
    header = [(h.strip() or f"column_{i + 1}")[:100] for i, h in enumerate(rows[0][:MAX_COLS])]
    width = len(header)
    body = [[c[:MAX_CELL] for c in (r + [""] * width)[:width]] for r in rows[1:]]
    return dedupe_header(header), body


def dedupe_header(cols: list[str]) -> list[str]:
    seen: Counter[str] = Counter()
    out = []
    for c in cols:
        seen[c] += 1
        out.append(c if seen[c] == 1 else f"{c}_{seen[c]}")
    return out


def clean(rows: list[list[str]], trim: bool, drop_empty: bool, dedupe: bool) -> list[list[str]]:
    out = [[c.strip() for c in r] for r in rows] if trim else rows
    if drop_empty:
        out = [r for r in out if any(c.strip() for c in r)]
    if dedupe:
        seen: set[tuple[str, ...]] = set()
        uniq = []
        for r in out:
            if (t := tuple(r)) not in seen:
                seen.add(t)
                uniq.append(r)
        out = uniq
    return out


def profile(columns: list[str], rows: list[list[str]]) -> list[dict[str, object]]:
    result = []
    for i, name in enumerate(columns):
        values = [r[i] for r in rows]
        present = [v for v in values if v.strip()]
        nums = [n for v in present if (n := _num(v)) is not None]
        numeric = bool(present) and len(nums) / len(present) >= 0.9
        col: dict[str, object] = {
            "name": name,
            "type": "number" if numeric else "text",
            "count": len(present),
            "missing": len(values) - len(present),
        }
        if numeric and nums:
            col.update(min=min(nums), max=max(nums), mean=round(statistics.fmean(nums), 6),
                       median=statistics.median(nums), sum=round(sum(nums), 6),
                       std=round(statistics.pstdev(nums), 6))  # fmt: skip
        else:
            col["unique"] = len(set(present))
            col["top"] = Counter(present).most_common(5)
        result.append(col)
    return result


def chart(
    columns: list[str], rows: list[list[str]], x: str, y: str | None, agg: Agg, limit: int = 50
) -> list[dict[str, object]]:
    if x not in columns or (y is not None and y not in columns):
        raise AppError("unknown_column", "Choose columns that exist in the table.", 400)
    xi = columns.index(x)
    yi = columns.index(y) if y else None
    groups: defaultdict[str, list[float]] = defaultdict(list)
    for r in rows:
        key = r[xi].strip() or "(blank)"
        if yi is None or agg == "count":
            groups[key].append(1.0)
        elif (n := _num(r[yi])) is not None:
            groups[key].append(n)
    fns: dict[str, Callable[[list[float]], float]] = {
        "sum": sum, "mean": statistics.fmean, "count": len, "min": min, "max": max,
    }  # fmt: skip
    fn = fns[agg]
    points = [{"x": k, "y": round(float(fn(v)), 6)} for k, v in groups.items() if v]
    if all(_num(p["x"]) is not None for p in points):  # type: ignore[arg-type]
        points.sort(key=lambda p: _num(p["x"]) or 0)  # type: ignore[arg-type]
    else:
        points.sort(key=lambda p: -p["y"])  # type: ignore[operator]
    return points[:limit]


def export(columns: list[str], rows: list[list[str]], fmt: Literal["csv", "xlsx"]) -> bytes:
    if fmt == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(columns)
        w.writerows([[_safe(c) for c in r] for r in rows])
        return buf.getvalue().encode("utf-8-sig")
    from openpyxl import Workbook

    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Data")
    ws.append(columns)
    for r in rows:
        ws.append([n if (n := _num(c)) is not None else _safe(c) for c in r])
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def _safe(v: str) -> str:
    """Neutralise spreadsheet formula injection in exported text cells."""
    return "'" + v if v[:1] in ("=", "+", "-", "@") and _num(v) is None else v
