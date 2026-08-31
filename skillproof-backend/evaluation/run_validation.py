# Task 6: Early validation script — confirms tier separation before building further
"""
Early validation gate for the SkillProof TPR scorer.

Run from the skillproof-backend directory:
    python -m evaluation.run_validation

What it does:
1. Reads evaluation/labeled_profiles.csv (username, tier columns)
2. Fetches GitHub data for each username (uses TTL cache — safe to re-run)
3. Extracts features using FeatureExtractor
4. Scores with TPRScorer
5. Prints a per-profile table and tier separation analysis
6. PASSES the gate if strong_avg > mid_avg > beginner_avg

This must pass before Task 7 (async jobs + analysis pipeline) is built.
"""
from __future__ import annotations

import csv
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Suppress noisy info logs during validation run
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def run() -> bool:
    """Run the validation and return True if the gate passes."""
    csv_path = Path(__file__).parent / "labeled_profiles.csv"
    if not csv_path.exists():
        print("ERROR: labeled_profiles.csv not found")
        return False

    from services.feature_extractor import FeatureExtractor
    from services.github_fetcher import GitHubFetcher
    from services.tpr_scorer import TPRScorer

    fetcher = GitHubFetcher()
    extractor = FeatureExtractor()
    scorer = TPRScorer()

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Filter out blank rows
    rows = [r for r in rows if r.get("username", "").strip()]

    if not rows:
        print("ERROR: labeled_profiles.csv is empty — add profiles first.")
        return False

    print(f"\nRunning validation on {len(rows)} profiles...\n")
    print(f"{'Username':<25} {'Tier':<10} {'TPR Score':<12} {'Confidence':<12} Status")
    print("-" * 72)

    results = []
    for i, row in enumerate(rows):
        username = row["username"].strip()
        tier = row["tier"].strip()
        try:
            github_data = fetcher.get_user_data(username)
            features = extractor.extract_all_features(github_data)
            tpr_score, confidence, breakdown = scorer.score(features)
            results.append(
                {"username": username, "tier": tier, "tpr_score": tpr_score, "confidence": confidence}
            )
            print(f"{username:<25} {tier:<10} {tpr_score:<12.1f} {confidence:<12} OK")
        except Exception as exc:
            print(f"{username:<25} {tier:<10} {'ERROR':<12} {'':12} {exc}")
            logger.debug("Error for %s", username, exc_info=True)

        # Polite delay — respect GitHub's rate limits
        if i < len(rows) - 1:
            time.sleep(2)

    if not results:
        print("\nNo results — check your GITHUB_TOKEN and labeled_profiles.csv.")
        return False

    # ------------------------------------------------------------------
    # Tier separation analysis
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("TIER SEPARATION ANALYSIS")
    print("=" * 72)

    tier_scores: dict = defaultdict(list)
    for r in results:
        tier_scores[r["tier"]].append(r["tpr_score"])

    tier_stats: dict = {}
    for tier in ["strong", "mid", "beginner"]:
        scores = tier_scores.get(tier, [])
        if scores:
            tier_stats[tier] = {
                "n": len(scores),
                "avg": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
            }
            s = tier_stats[tier]
            print(
                f"  {tier:<10} n={s['n']:<4} "
                f"avg={s['avg']:.1f}  "
                f"min={s['min']:.1f}  "
                f"max={s['max']:.1f}"
            )
        else:
            print(f"  {tier:<10} no data")

    # ------------------------------------------------------------------
    # Gate check
    # ------------------------------------------------------------------
    print("\n" + "=" * 72)

    strong_avg = tier_stats.get("strong", {}).get("avg", 0.0)
    mid_avg = tier_stats.get("mid", {}).get("avg", 0.0)
    beginner_avg = tier_stats.get("beginner", {}).get("avg", 0.0)

    gate_pass = True
    issues = []

    if "strong" in tier_stats and "mid" in tier_stats:
        if strong_avg <= mid_avg:
            gate_pass = False
            issues.append(
                f"FAIL: strong avg ({strong_avg:.1f}) <= mid avg ({mid_avg:.1f})"
            )
        else:
            print(f"  PASS: strong ({strong_avg:.1f}) > mid ({mid_avg:.1f})")

    if "mid" in tier_stats and "beginner" in tier_stats:
        if mid_avg <= beginner_avg:
            gate_pass = False
            issues.append(
                f"FAIL: mid avg ({mid_avg:.1f}) <= beginner avg ({beginner_avg:.1f})"
            )
        else:
            print(f"  PASS: mid ({mid_avg:.1f}) > beginner ({beginner_avg:.1f})")

    print()
    if gate_pass:
        print("VALIDATION GATE: PASSED")
        print("Tier separation is sufficient. Proceed to Task 7.")
    else:
        print("VALIDATION GATE: FAILED")
        for issue in issues:
            print(f"  {issue}")
        print("\nDo NOT proceed to Task 7 until the gate passes.")
        print("Fix: review TPR scorer weights or feature extraction.")

    print("=" * 72 + "\n")
    return gate_pass


if __name__ == "__main__":
    passed = run()
    sys.exit(0 if passed else 1)
