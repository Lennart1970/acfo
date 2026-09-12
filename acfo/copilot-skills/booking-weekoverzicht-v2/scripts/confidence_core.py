"""Booking Confidence signal math. No network.

Same module is imported by the CLI engine and copied into the Copilot Studio
skill zip. Callers must already have purchase rows (Excel upload or fetched
JSON) and pass them as a case file. The model must not invent GL/VAT/amount.
"""
from __future__ import annotations

import re
import statistics
from collections import Counter
from datetime import date

COST_GL_TYPES = {"110", "111", "120", "121", "122", "125"}
AP_GL_CODES = {"1300", "1600"}
VAT_GL_CODES = {"1450", "1400", "1410", "1420"}

DEFAULT_CONFIG = {
    "thresholds": {"auto": 0.9, "ai_review": 0.6},
    "weights": {
        "known_supplier": 10,
        "booked_before": 15,
        "gl_consistent": 20,
        "vat_consistent": 15,
        "amount_in_range": 10,
        "cadence_consistent": 5,
        "description_similar": 5,
        "currency_payment_normal": 10,
        "no_unusual_change": 10,
    },
    "amount_band": 0.5,
    "desc_min_sim": 0.3,
}

CORE_SIGNALS = [
    "known_supplier",
    "booked_before",
    "gl_consistent",
    "vat_consistent",
    "amount_in_range",
    "cadence_consistent",
    "description_similar",
    "currency_payment_normal",
]


def tokenize(text):
    return set(t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) > 2)


def modal(values):
    """Most common value. A tie is None — never pick a random GL/VAT."""
    if not values:
        return None
    counts = Counter(values)
    highest = max(counts.values())
    winners = [value for value, count in counts.items() if count == highest]
    return winners[0] if len(winners) == 1 else None


def is_cost_line(line: dict) -> bool:
    gl_type = str(line.get("glAccountType") or "").strip()
    gl_code = str(line.get("glAccountCode") or "").strip()
    line_number = str(line.get("lineNumber") or "").strip()
    return (
        gl_type in COST_GL_TYPES
        and gl_code not in AP_GL_CODES
        and gl_code not in VAT_GL_CODES
        and line_number != "9999"
    )


def is_balance_line(line: dict) -> bool:
    gl_code = str(line.get("glAccountCode") or "").strip()
    line_number = str(line.get("lineNumber") or "").strip()
    gl_type = str(line.get("glAccountType") or "").strip()
    return (
        gl_code in AP_GL_CODES
        or gl_code in VAT_GL_CODES
        or line_number == "9999"
        or gl_type == "22"
    )


def cost_lines(lines: list | None) -> list[dict]:
    """GL/VAT comparison uses cost lines only.

    Invantive exports carry Grootboekrekeningsoort; then require a cost type.
    Simple one-line Exact exports have no type — drop AP/VAT by code instead.
    """
    rows = list(lines or [])
    if any(str(ln.get("glAccountType") or "").strip() for ln in rows):
        return [ln for ln in rows if is_cost_line(ln)]
    return [ln for ln in rows if not is_balance_line(ln)]


def _iso_day(value):
    if not value:
        return None
    return str(value)[:10]


def merge_config(config: dict | None = None) -> dict:
    overlay = config or {}
    return {
        "thresholds": {**DEFAULT_CONFIG["thresholds"], **(overlay.get("thresholds") or {})},
        "weights": {**DEFAULT_CONFIG["weights"], **(overlay.get("weights") or {})},
        "amount_band": overlay.get("amount_band", DEFAULT_CONFIG["amount_band"]),
        "desc_min_sim": overlay.get("desc_min_sim", DEFAULT_CONFIG["desc_min_sim"]),
    }


def score_case(case: dict, config: dict | None = None) -> dict:
    """Score one purchase entry from an already-loaded case file.

    Required keys:
      entry: dict (purchase header)
      lines: list (current booking lines)
      history: list of prior purchase headers (current entry excluded)
      history_lines: list of lines from up to 3 recent historical entries
      accounts_count: int (Excel v2: 1 when supplier name is present)
    """
    cfg = merge_config(config)

    entry = case.get("entry") or {}
    lines = case.get("lines") or []
    history = list(case.get("history") or [])
    history_lines = list(case.get("history_lines") or [])
    known = int(case.get("accounts_count") or 0) > 0

    supplier_name = (entry.get("supplierName") or "").strip()
    current_cost = cost_lines(lines)
    historical_cost = cost_lines(history_lines)
    primary = current_cost[0] if current_cost else (lines[0] if lines else {})
    cur_gl = str(primary.get("glAccountCode") or "").strip()
    cur_vat = str(primary.get("vatCode") or "").strip()
    cur_amount = abs(entry.get("amountDC") or 0)
    cur_currency = entry.get("currency") or ""
    cur_paycond = entry.get("paymentCondition") or ""
    cur_desc = entry.get("description") or ""
    cur_date = _iso_day(entry.get("entryDate"))

    hist_gls = [str(l.get("glAccountCode") or "").strip() for l in historical_cost if l.get("glAccountCode")]
    hist_vats = [str(l.get("vatCode") or "").strip() for l in historical_cost if l.get("vatCode")]
    hist_amounts = [abs(h.get("amountDC") or 0) for h in history if h.get("amountDC")]
    hist_dates = sorted(d for d in (_iso_day(h.get("entryDate")) for h in history) if d)
    hist_currencies = [h.get("currency") for h in history if h.get("currency")]
    hist_payconds = [h.get("paymentCondition") for h in history if h.get("paymentCondition")]

    s = {}
    s["known_supplier"] = known
    s["booked_before"] = len(history) > 0
    s["gl_consistent"] = bool(hist_gls) and cur_gl == modal(hist_gls)
    s["vat_consistent"] = bool(hist_vats) and cur_vat == modal(hist_vats)
    if hist_amounts:
        band = cfg["amount_band"]
        lo, hi = min(hist_amounts) * (1 - band), max(hist_amounts) * (1 + band)
        s["amount_in_range"] = lo <= cur_amount <= hi
    else:
        s["amount_in_range"] = False
    if len(hist_dates) >= 2 and cur_date:
        gaps = [
            (date.fromisoformat(hist_dates[i + 1]) - date.fromisoformat(hist_dates[i])).days
            for i in range(len(hist_dates) - 1)
        ]
        med = statistics.median(gaps) if gaps else 0
        since_last = (date.fromisoformat(cur_date) - date.fromisoformat(hist_dates[-1])).days
        s["cadence_consistent"] = med == 0 or since_last <= max(2 * med, 45)
    else:
        s["cadence_consistent"] = len(history) == 1
    if history:
        ref = tokenize(history[0].get("description"))
        cur = tokenize(cur_desc)
        sim = len(cur & ref) / len(cur | ref) if (cur | ref) else 0
        s["description_similar"] = sim >= cfg["desc_min_sim"]
    else:
        sim = 0
        s["description_similar"] = False
    s["currency_payment_normal"] = (
        (not hist_currencies or cur_currency == modal(hist_currencies))
        and (not hist_payconds or cur_paycond == modal(hist_payconds))
    )
    s["no_unusual_change"] = s["gl_consistent"] and s["vat_consistent"] and s["amount_in_range"]

    agreement = sum(1 for k in CORE_SIGNALS if s[k]) / len(CORE_SIGNALS)
    s["signals_agree"] = agreement >= 0.75

    weights = cfg["weights"]
    earned = sum(weights.get(k, 0) for k in weights if s.get(k))
    confidence = round(earned / 100.0, 4)

    th = cfg["thresholds"]
    if not s["known_supplier"] or not s["signals_agree"]:
        route = "Human Review"
    elif confidence >= th["auto"]:
        route = "Auto"
    elif confidence >= th["ai_review"]:
        route = "AI Review"
    else:
        route = "Human Review"

    return {
        "entry": entry,
        "lines": lines,
        "signals": s,
        "agreement": agreement,
        "confidence": confidence,
        "route": route,
        "evidence": {
            "supplier": supplier_name,
            "supplier_known": known,
            "history_count": len(history),
            "history_amounts": hist_amounts[:10],
            "history_dates": hist_dates[-10:],
            "current": {
                "gl": cur_gl,
                "vat": cur_vat,
                "amount": cur_amount,
                "currency": cur_currency,
                "paymentCondition": cur_paycond,
            },
            "historical_modal": {
                "gl": modal(hist_gls),
                "vat": modal(hist_vats),
                "currency": modal(hist_currencies),
                "paymentCondition": modal(hist_payconds),
            },
            "description_similarity": round(sim, 3),
            "thresholds": th,
            "weights": weights,
        },
    }


def score_cases(cases: list, config: dict | None = None) -> list:
    return [score_case(c, config) for c in cases]
