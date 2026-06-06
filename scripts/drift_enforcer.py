#!/usr/bin/env python3
"""
Universal Drift Enforcer

Reads registry JSON files from docs/drift_registries/ and compares each
entry's `verified_commit` against the file's latest git commit hash.

Usage:
  python3 scripts/drift_enforcer.py                 # Check all domains
  python3 scripts/drift_enforcer.py --domain api    # Check one domain
  python3 scripts/drift_enforcer.py --stamp         # Stamp current hashes
  python3 scripts/drift_enforcer.py --coverage      # Report coverage
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

REGISTRIES_DIR = Path(__file__).resolve().parent.parent / "docs" / "drift_registries"
REPO_ROOT = Path(__file__).resolve().parent.parent


def git_latest_commit(filepath: str) -> str | None:
    """Return the full SHA of the last commit that touched `filepath`."""
    abs_path = REPO_ROOT / filepath
    if not abs_path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H", "-1", "--", filepath],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        sha = result.stdout.strip()
        return sha if sha else None
    except Exception:
        return None


def load_registry(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_registry(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def stamp_hashes(reg_path: Path, registry: dict) -> None:
    """Write the current git hash of each source file into the registry."""
    count = 0
    for entry in registry.get("entries", []):
        sha = git_latest_commit(entry["source_file"])
        if sha:
            entry["verified_commit"] = sha
            count += 1
    if "_meta" not in registry:
        registry["_meta"] = {}
    registry["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_registry(reg_path, registry)
    print(f"✅ [{reg_path.stem.upper()}] Stamped {count} entries.")


def check_drift(domain: str, registry: dict) -> bool:
    """Compare verified_commit against current HEAD. Returns True if drift found."""
    entries = registry.get("entries", [])
    if not entries:
        return False

    drifted, clean, missing, unstamped = [], [], [], []

    for entry in entries:
        source = entry["source_file"]
        verified = entry.get("verified_commit")
        current = git_latest_commit(source)

        if current is None:
            missing.append(entry)
        elif verified is None:
            unstamped.append({**entry, "current_commit": current})
        elif verified != current:
            drifted.append({**entry, "current_commit": current})
        else:
            clean.append(entry)

    # Print report
    total = len(entries)
    print(f"\n{'=' * 72}")
    print(f"  DRIFT REPORT: {domain.upper()}")
    print(f"{'=' * 72}")
    print(f"  Tracked: {total}  ✅ Clean: {len(clean)}  "
          f"⚠️  Drifted: {len(drifted)}  ❓ Unstamped: {len(unstamped)}  "
          f"❌ Missing: {len(missing)}")

    if drifted:
        print(f"\n{'-' * 72}")
        print("  ⚠️  DRIFTED FILES — Dependencies need review")
        print(f"{'-' * 72}")
        for entry in drifted:
            print(f"\n  📄 {entry['source_file']}")
            print(f"     verified: {entry['verified_commit'][:10]}  →  "
                  f"current: {entry['current_commit'][:10]}")
            for dep in entry.get("dependencies", []):
                print(f"       📎 [{dep['type'].upper()}] {dep['path']}")
                print(f"         └─ {dep['reason']}")

    if unstamped:
        print(f"\n{'-' * 72}")
        print("  ❓ UNSTAMPED — Run with --stamp to initialize")
        print(f"{'-' * 72}")
        for entry in unstamped:
            print(f"  📄 {entry['source_file']}  "
                  f"(current: {entry['current_commit'][:10]})")

    if missing:
        print(f"\n{'-' * 72}")
        print("  ❌ MISSING — Files no longer exist")
        print(f"{'-' * 72}")
        for entry in missing:
            print(f"  📄 {entry['source_file']}")

    if not drifted and not unstamped and not missing:
        print(f"\n  ✅ All {total} files in '{domain}' are clean.")

    print(f"{'=' * 72}")
    return bool(drifted or unstamped or missing)


def report_coverage() -> None:
    """Report what percentage of repo files are tracked."""
    tracked = set()
    for reg_path in REGISTRIES_DIR.glob("*.json"):
        try:
            for entry in load_registry(reg_path).get("entries", []):
                tracked.add(entry["source_file"])
        except Exception:
            pass

    result = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True,
        cwd=REPO_ROOT, check=True,
    )
    skip_ext = {".png", ".svg", ".ico", ".jpg", ".jpeg", ".gif", ".webp"}
    skip_names = {"package-lock.json", "uv.lock"}
    eligible = {
        f for f in result.stdout.splitlines()
        if Path(f).suffix.lower() not in skip_ext
        and Path(f).name not in skip_names
        and not f.startswith("public/")
    }
    covered = eligible & tracked
    pct = (len(covered) / len(eligible) * 100) if eligible else 0

    print(f"{'=' * 72}")
    print(f"  DRIFT COVERAGE: {len(covered)}/{len(eligible)} files ({pct:.1f}%)")
    print(f"{'=' * 72}")
    if eligible - tracked:
        print("  Top untracked:")
        for f in sorted(eligible - tracked)[:10]:
            print(f"    📄 {f}")
    print(f"{'=' * 72}")


def main():
    parser = argparse.ArgumentParser(description="Universal Drift Enforcer")
    parser.add_argument("--domain", help="Check a specific domain")
    parser.add_argument("--stamp", action="store_true", help="Stamp current hashes")
    parser.add_argument("--coverage", action="store_true", help="Report coverage")
    args = parser.parse_args()

    if not REGISTRIES_DIR.exists():
        print(f"❌ Registry directory not found: {REGISTRIES_DIR}")
        sys.exit(1)

    if args.coverage:
        report_coverage()
        sys.exit(0)

    if args.domain:
        files = [REGISTRIES_DIR / f"{args.domain}.json"]
        if not files[0].exists():
            print(f"❌ Domain not found: {files[0]}")
            sys.exit(1)
    else:
        files = sorted(REGISTRIES_DIR.glob("*.json"))

    overall_drift = False
    for reg_path in files:
        registry = load_registry(reg_path)
        if args.stamp:
            stamp_hashes(reg_path, registry)
        else:
            if check_drift(reg_path.stem, registry):
                overall_drift = True

    if not args.stamp:
        if overall_drift:
            print("\n  🚨 Drift detected. Review and run --stamp when ready.\n")
            sys.exit(1)
        else:
            print("\n  🌟 All domains clean. Zero drift.\n")


if __name__ == "__main__":
    main()
