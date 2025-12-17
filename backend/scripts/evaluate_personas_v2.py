"""evaluate_personas_v2.py

Run the 100 generated personas against the V2 recommendations endpoint
and print a quick scoring distribution + expectation failures.

Why this exists
- We already generate personas in `backend/scripts/generate_personas.py`
- We already store them in `backend/scenarios/generated_personas.json`
- This script uses those personas to *measure* real scoring output from:
    POST /api/v2/recommendations

Usage (local backend running):
    python backend/scripts/evaluate_personas_v2.py

Usage (production Render):
    python backend/scripts/evaluate_personas_v2.py --base-url https://smartrip-api.onrender.com

Notes
- Requires: requests (already in backend/requirements.txt)
- Output is console-friendly for a quick glance.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


def _percentile(sorted_vals: List[float], p: float) -> Optional[float]:
    if not sorted_vals:
        return None
    if p <= 0:
        return float(sorted_vals[0])
    if p >= 100:
        return float(sorted_vals[-1])

    # Linear interpolation between closest ranks
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return float(d0 + d1)


def _bucket(score: float) -> str:
    if score < 25:
        return "0-24"
    if score < 50:
        return "25-49"
    if score < 70:
        return "50-69"
    if score < 85:
        return "70-84"
    return "85-100"


def _load_personas(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("generated_personas.json must contain a list")
    return data


def _call_v2(base_url: str, preferences: Dict[str, Any], timeout: int) -> Tuple[int, Dict[str, Any], int]:
    """Return (status_code, json_body_or_error, response_time_ms)."""
    url = base_url.rstrip("/") + "/api/v2/recommendations"

    start = time.time()
    resp = requests.post(url, json=preferences, timeout=timeout)
    elapsed_ms = int((time.time() - start) * 1000)

    try:
        payload = resp.json()
    except Exception:
        payload = {"success": False, "error": resp.text}

    return resp.status_code, payload, elapsed_ms


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate 100 personas against V2 recommendations")
    parser.add_argument(
        "--base-url",
        default="http://localhost:5000",
        help="Backend base URL (default: http://localhost:5000)",
    )
    parser.add_argument(
        "--personas",
        default=str(Path(__file__).resolve().parents[1] / "scenarios" / "generated_personas.json"),
        help="Path to generated_personas.json",
    )
    parser.add_argument("--max-personas", type=int, default=100, help="How many personas to evaluate")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout seconds")
    args = parser.parse_args()

    personas_path = Path(args.personas)
    personas = _load_personas(personas_path)[: max(0, args.max_personas)]

    print("=" * 88)
    print("V2 PERSONA SCORING EVALUATION")
    print("=" * 88)
    print(f"Base URL: {args.base_url}")
    print(f"Personas: {personas_path} (loaded {len(personas)})")
    print("Endpoint: POST /api/v2/recommendations")
    print("=" * 88)

    totals = {
        "total": 0,
        "http_ok": 0,
        "api_success": 0,
        "with_results": 0,
        "zero_results": 0,
        "http_errors": 0,
        "api_errors": 0,
    }

    response_times: List[int] = []
    top_scores: List[float] = []

    failures_min_results: List[Tuple[int, str, int, int]] = []
    failures_min_score: List[Tuple[int, str, float, float]] = []

    bucket_counts: Dict[str, int] = {"0-24": 0, "25-49": 0, "50-69": 0, "70-84": 0, "85-100": 0}

    for idx, persona in enumerate(personas, start=1):
        totals["total"] += 1

        persona_id = int(persona.get("id") or idx)
        name = str(persona.get("name") or f"Persona {persona_id}")
        preferences = persona.get("preferences") or {}

        expected_min_results = int(persona.get("expected_min_results") or 0)
        expected_min_top_score = persona.get("expected_min_top_score")
        expected_min_top_score_f = float(expected_min_top_score) if expected_min_top_score is not None else None

        status, payload, ms = _call_v2(args.base_url, preferences, timeout=args.timeout)
        response_times.append(ms)

        if status != 200:
            totals["http_errors"] += 1
            if idx <= 5:
                print(f"[HTTP {status}] {persona_id} {name} -> {payload.get('error')}")
            continue

        totals["http_ok"] += 1

        if not payload.get("success", False):
            totals["api_errors"] += 1
            if idx <= 5:
                print(f"[API error] {persona_id} {name} -> {payload.get('error')}")
            continue

        totals["api_success"] += 1

        results = payload.get("data") or []
        count = int(payload.get("count") or len(results))
        if count <= 0:
            totals["zero_results"] += 1
            if expected_min_results > 0:
                failures_min_results.append((persona_id, name, count, expected_min_results))
            continue

        totals["with_results"] += 1

        top = results[0].get("match_score")
        if top is None:
            # defensive; treat as 0
            top_score = 0.0
        else:
            top_score = float(top)

        top_scores.append(top_score)
        bucket_counts[_bucket(top_score)] += 1

        # Expectation checks
        if count < expected_min_results:
            failures_min_results.append((persona_id, name, count, expected_min_results))

        if expected_min_top_score_f is not None and top_score < expected_min_top_score_f:
            failures_min_score.append((persona_id, name, top_score, expected_min_top_score_f))

        # lightweight progress
        if idx % 20 == 0:
            print(f"... processed {idx}/{len(personas)} personas")

    # Summary
    print("\n" + "-" * 88)
    print("SUMMARY")
    print("-" * 88)
    print(f"Total personas:      {totals['total']}")
    print(f"HTTP 200:           {totals['http_ok']}")
    print(f"API success:        {totals['api_success']}")
    print(f"With results:       {totals['with_results']}")
    print(f"Zero results:       {totals['zero_results']}")
    print(f"HTTP errors:        {totals['http_errors']}")
    print(f"API errors:         {totals['api_errors']}")

    if response_times:
        print(
            "Response time (ms): "
            f"avg={int(statistics.mean(response_times))} "
            f"p50={int(_percentile(sorted(response_times), 50) or 0)} "
            f"p90={int(_percentile(sorted(response_times), 90) or 0)}"
        )

    if top_scores:
        s = sorted(top_scores)
        print(
            "Top score stats:    "
            f"min={s[0]:.0f} "
            f"p10={(_percentile(s, 10) or 0):.0f} "
            f"p25={(_percentile(s, 25) or 0):.0f} "
            f"p50={(_percentile(s, 50) or 0):.0f} "
            f"p75={(_percentile(s, 75) or 0):.0f} "
            f"p90={(_percentile(s, 90) or 0):.0f} "
            f"max={s[-1]:.0f} "
            f"avg={statistics.mean(top_scores):.1f}"
        )

        print("\nHistogram (top score buckets):")
        for b in ["0-24", "25-49", "50-69", "70-84", "85-100"]:
            print(f"  {b:>6}: {bucket_counts[b]}")

    # Expectation failures (top few)
    if failures_min_results:
        failures_min_results.sort(key=lambda x: (x[2] - x[3], x[0]))
        print("\nFailures vs expected_min_results (worst 10):")
        for persona_id, name, got, expected in failures_min_results[:10]:
            print(f"  [{persona_id}] {name}: got {got}, expected >= {expected}")

    if failures_min_score:
        failures_min_score.sort(key=lambda x: (x[2] - x[3], x[0]))
        print("\nFailures vs expected_min_top_score (worst 10):")
        for persona_id, name, got, expected in failures_min_score[:10]:
            print(f"  [{persona_id}] {name}: top_score {got:.0f}, expected >= {expected:.0f}")

    print("\nDone.")

    # non-zero exit if endpoint is failing badly
    if totals["http_ok"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
