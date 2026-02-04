import csv
import glob
import os
from datetime import datetime

OUTPUT_FILE = "jobs_all.csv"

# Known input files
INPUT_FILES = [
    "google_jobs.csv",
    "jobs_indeed_reed.csv",
] + glob.glob("data_*.csv")

STANDARD_HEADERS = [
    "Source",
    "Title",
    "Company",
    "Location",
    "Posted Time",
    "Job Link",
    "Collected At",
]


def normalize_row(source, title, company, location, posted_time, job_link, collected_at):
    return [
        source.strip(),
        title.strip(),
        company.strip(),
        location.strip(),
        posted_time.strip(),
        job_link.strip(),
        collected_at.strip(),
    ]


def row_key(row):
    # Deduplicate by title + company + location
    return "|".join([
        row[1].lower(),
        row[2].lower(),
        row[3].lower(),
    ])


def has_header(row):
    row_lower = [c.lower() for c in row]
    return "title" in row_lower and "company" in row_lower


def read_google_s(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        first = next(reader, None)
        if not first:
            return rows
        if has_header(first):
            for r in reader:
                if len(r) < 5:
                    continue
                rows.append(normalize_row(
                    "google",
                    r[0], r[1], r[2], r[3], r[4], ""
                ))
        else:
            # No header; assume google_s layout
            r = first
            if len(r) >= 5:
                rows.append(normalize_row("google", r[0], r[1], r[2], r[3], r[4], ""))
            for r in reader:
                if len(r) < 5:
                    continue
                rows.append(normalize_row("google", r[0], r[1], r[2], r[3], r[4], ""))
    return rows


def read_indeed_reed(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        first = next(reader, None)
        if not first:
            return rows
        if has_header(first):
            for r in reader:
                if len(r) < 6:
                    continue
                rows.append(normalize_row(
                    r[0], r[1], r[2], r[3], r[4], r[5], ""
                ))
        else:
            r = first
            if len(r) >= 6:
                rows.append(normalize_row(r[0], r[1], r[2], r[3], r[4], r[5], ""))
            for r in reader:
                if len(r) < 6:
                    continue
                rows.append(normalize_row(r[0], r[1], r[2], r[3], r[4], r[5], ""))
    return rows


def read_data_recorder(path):
    # Expected tuple: (source_label, num, title, company, location, posted_time, link)
    rows = []
    collected_at = ""
    try:
        base = os.path.basename(path)
        # data_04-Feb-2026.csv -> 04-Feb-2026
        collected_at = base.replace("data_", "").replace(".csv", "")
        # normalize to ISO if possible
        collected_at = datetime.strptime(collected_at, "%d-%b-%Y").date().isoformat()
    except Exception:
        collected_at = ""

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        first = next(reader, None)
        if not first:
            return rows
        if has_header(first):
            # Try to map by header names if present
            headers = [h.lower() for h in first]
            def idx(name):
                return headers.index(name) if name in headers else None

            i_source = idx("source")
            i_title = idx("title")
            i_company = idx("company")
            i_location = idx("location")
            i_posted = idx("posted time") if "posted time" in headers else idx("posted")
            i_link = idx("job link") if "job link" in headers else idx("link")

            for r in reader:
                if i_title is None or i_company is None or i_location is None:
                    continue
                rows.append(normalize_row(
                    r[i_source] if i_source is not None else "google",
                    r[i_title],
                    r[i_company],
                    r[i_location],
                    r[i_posted] if i_posted is not None else "",
                    r[i_link] if i_link is not None else "",
                    collected_at,
                ))
        else:
            # No header; assume tuple order
            r = first
            if len(r) >= 7:
                rows.append(normalize_row(
                    r[0], r[2], r[3], r[4], r[5], r[6], collected_at
                ))
            for r in reader:
                if len(r) < 7:
                    continue
                rows.append(normalize_row(
                    r[0], r[2], r[3], r[4], r[5], r[6], collected_at
                ))
    return rows


def main():
    combined = []

    for path in INPUT_FILES:
        if not os.path.exists(path):
            continue
        lower = path.lower()
        if lower == "google_jobs.csv":
            combined.extend(read_google_s(path))
        elif lower == "jobs_indeed_reed.csv":
            combined.extend(read_indeed_reed(path))
        elif lower.startswith("data_"):
            combined.extend(read_data_recorder(path))

    # Deduplicate
    seen = set()
    deduped = []
    for row in combined:
        key = row_key(row)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(STANDARD_HEADERS)
        for row in deduped:
            writer.writerow(row)

    print(f"Merged {len(combined)} rows into {len(deduped)} unique rows -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
