#!/usr/bin/env python3
"""Excel v2 booking review: list weeks, then score one ISO week. No network."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from confidence_core import DEFAULT_CONFIG, score_case
from excel_transactions import build_cases, entries_in_week, list_weeks, load_entries
from write_weekoverzicht import outcome_text, scored_row, write_xlsx


def weeks_payload(bundle: dict) -> dict:
    weeks = list_weeks(bundle)
    return {
        "needs_week": True,
        "ask": "Welke week wil je reviewen?",
        "source": bundle.get("source"),
        "sourceName": bundle.get("sourceName"),
        "administrationCode": bundle.get("administrationCode") or "",
        "entries_in_file": len(bundle.get("entries") or []),
        "weeks": weeks,
    }


def review_week(bundle: dict, week: str, config=None) -> dict:
    meta, matched = entries_in_week(bundle, week)
    cases = build_cases(bundle, matched)
    results = []
    rows = []
    counts = {"Auto": 0, "AI Review": 0, "Human Review": 0}
    for case in cases:
        scored = score_case(case, config)
        row = scored_row(scored)
        rows.append(row)
        counts[scored["route"]] = counts.get(scored["route"], 0) + 1
        results.append(
            {
                "entryNumber": row["Boekstuk"],
                "date": row["Datum"],
                "supplier": row["Leverancier"],
                "amount": row["Bedrag"],
                "route": scored["route"],
                "confidence": scored["confidence"],
                "signals": scored["signals"],
                "failed_signals": row["Signalen"],
                "outcome": outcome_text(scored),
            }
        )
    return {
        "needs_week": False,
        "week": meta["week"],
        "label": meta["label"],
        "start": meta["start"].isoformat(),
        "end": meta["end"].isoformat(),
        "administrationCode": bundle.get("administrationCode") or "",
        "source": bundle.get("source"),
        "sourceName": bundle.get("sourceName"),
        "entries_in_file": len(bundle.get("entries") or []),
        "entries": len(results),
        "counts": counts,
        "results": results,
        "rows": rows,
        "weeks": list_weeks(bundle),
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Review Exact purchase Excel for one ISO week (v2, no Exact calls)"
    )
    p.add_argument("--input", required=True, help="uploaded Exact transaction .xlsx")
    p.add_argument(
        "--week",
        default="",
        help="ISO week (2026-W37), 'week 37', or a date in that week. Omit to list weeks.",
    )
    p.add_argument("--output", default="", help="xlsx path")
    p.add_argument("--json", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    bundle = load_entries(args.input)
    if not args.week:
        payload = weeks_payload(bundle)
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 3
    summary = review_week(bundle, args.week, DEFAULT_CONFIG)
    out = (
        Path(args.output)
        if args.output
        else Path(f"Weekoverzicht-{summary['week']}.xlsx")
    )
    write_xlsx(out, summary)
    dump = {k: v for k, v in summary.items() if k != "rows"}
    dump["output"] = str(out)
    json.dump(dump, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if summary["entries"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
