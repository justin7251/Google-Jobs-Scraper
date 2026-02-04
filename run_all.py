import subprocess
import sys

SCRIPTS = [
    "google_s.py",
    "job_boards.py",
    "merge_jobs.py",
]


def run_script(name):
    result = subprocess.run([sys.executable, name])
    if result.returncode != 0:
        raise SystemExit(f"Failed running {name} (exit {result.returncode})")


def main():
    for script in SCRIPTS:
        run_script(script)


if __name__ == "__main__":
    main()
