#!/usr/bin/env python3
"""Score already-fetched Exact case files in the Copilot sandbox (no network).

Input JSON:
  { "date": "YYYY-MM-DD", "administrationCode": "...", "searched": 50,
    "cases": [ { "entry", "lines", "history", "history_lines", "accounts_count" }, ... ] }

Or a single case object with an "entry" key.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / "scripts"))

from confidence_core import DEFAULT_CONFIG, score_case
from write_dagoverzicht import flags_for, write_xlsx

SIGNAL_NL = {
    "known_supplier": "bekende leverancier",
    "booked_before": "eerder geboekt",
    "gl_consistent": "grootboek",
    "vat_consistent": "btw",
    "amount_in_range": "bedrag",
    "cadence_consistent": "timing",
    "description_similar": "omschrijving",
    "currency_payment_normal": "valuta/betaling",
    "no_unusual_change": "geen bijzondere afwijking",
    "signals_agree": "signalen eens",
}


def failed_signals(signals: dict) -> str:
    failed = [SIGNAL_NL.get(k, k) for k, v in signals.items() if k != "signals_agree" and not v]
    return ", ".join(failed)


def load_bundle(raw: dict) -> dict:
    if isinstance(raw.get("cases"), list):
        return raw
    if "entry" in raw:
        return {
            "date": str((raw.get("entry") or {}).get("entryDate") or "")[:10],
            "administrationCode": str((raw.get("entry") or {}).get("division") or ""),
            "searched": 1,
            "cases": [raw],
        }
    raise ValueError("JSON needs 'cases' array or a single case with 'entry'")


def scored_row(scored: dict) -> dict:
    entry = scored["entry"]
    lines = scored.get("lines") or []
    ev = scored["evidence"]
    vat = ev["current"].get("vat") or (lines[0].get("vatCode") if lines else "")
    gl = ev["current"].get("gl")
    return {
        "Datum": str(entry.get("entryDate") or "")[:10],
        "Boekstuk": str(entry.get("entryNumber") or ""),
        "Leverancier": ev.get("supplier") or "",
        "Bedrag": entry.get("amountDC"),
        "Valuta": entry.get("currency") or "",
        "Btw-code": vat or "",
        "Journaal": entry.get("journalCode") or entry.get("journal") or gl or "",
        "Betalingsconditie": entry.get("paymentCondition") or "",
        "Omschrijving": entry.get("description") or "",
        "Opvallend": flags_for(entry),
        "Route": scored["route"],
        "Confidence": scored["confidence"],
        "Signalen": failed_signals(scored["signals"]),
    }


def run(bundle: dict, config=None) -> dict:
    cases = bundle.get("cases") or []
    results = []
    rows = []
    counts = {"Auto": 0, "AI Review": 0, "Human Review": 0}
    for case in cases:
        scored = score_case(case, config)
        results.append({
            "entryNumber": str((scored["entry"] or {}).get("entryNumber") or ""),
            "supplier": scored["evidence"]["supplier"],
            "confidence": scored["confidence"],
            "route": scored["route"],
            "signals": scored["signals"],
        })
        counts[scored["route"]] = counts.get(scored["route"], 0) + 1
        rows.append(scored_row(scored))
    return {
        "date": bundle.get("date") or (rows[0]["Datum"] if rows else ""),
        "administrationCode": str(bundle.get("administrationCode") or ""),
        "searched": bundle.get("searched", len(cases)),
        "entries": len(results),
        "counts": counts,
        "results": results,
        "rows": rows,
    }


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Score booking case files; write Excel")
    p.add_argument("--input", required=True, help="case or cases JSON")
    p.add_argument("--output", default="", help="xlsx path")
    p.add_argument("--json", action="store_true")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    bundle = load_bundle(json.loads(Path(args.input).read_text(encoding="utf-8")))
    summary = run(bundle, DEFAULT_CONFIG)
    out = Path(args.output) if args.output else Path(f"BookingCheck-{summary['date'] or 'scored'}.xlsx")
    write_xlsx(
        out,
        summary["date"] or "1970-01-01",
        summary["administrationCode"],
        summary["searched"],
        summary["rows"],
        scored=True,
    )
    dump = {k: v for k, v in summary.items() if k != "rows"}
    dump["output"] = str(out)
    if args.json:
        json.dump(dump, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(json.dumps(dump, ensure_ascii=False, indent=2))
    return 0 if summary["entries"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
