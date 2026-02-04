import argparse
import subprocess
import sys

SCRIPTS = [
    "google_s.py",
    "job_boards.py",
    "merge_jobs.py",
]


def run_script(name, extra_args):
    result = subprocess.run([sys.executable, name, *extra_args])
    if result.returncode != 0:
        raise SystemExit(f"Failed running {name} (exit {result.returncode})")


def main():
    parser = argparse.ArgumentParser(description="Run all job scrapers and merge.")
    parser.add_argument("--query", default="php developer", help="Job title or keywords.")
    parser.add_argument(
        "--location",
        default="london,birmingham,coventry,manchester",
        help="Comma-separated job locations (e.g., london,birmingham).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1,
        help="Pages per board to scan (Indeed/Reed).",
    )
    args = parser.parse_args()

    common_args = ["--query", args.query, "--location", args.location]
    boards_args = [*common_args, "--max-pages", str(args.max_pages)]

    for script in SCRIPTS:
        if script == "job_boards.py":
            run_script(script, boards_args)
        elif script in {"google_s.py"}:
            run_script(script, common_args)
        else:
            run_script(script, [])


if __name__ == "__main__":
    main()
