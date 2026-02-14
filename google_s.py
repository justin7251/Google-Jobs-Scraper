from DrissionPage import ChromiumPage
import argparse
import csv
import time
import re
from urllib.parse import quote_plus

DEFAULT_QUERY = "php developer"
DEFAULT_LOCATIONS = ["london", "birmingham", "coventry", "manchester"]


def clean_text(value):
    if not value:
        return ""
    return " ".join(value.split())


def safe_text(ele):
    return clean_text(ele.text) if ele else ""


def safe_href(ele):
    return ele.attr("href") if ele else ""


def first_ele(parent, selectors, timeout=0.5):
    for sel in selectors:
        try:
            ele = parent.ele(sel, timeout=timeout)
        except Exception:
            ele = None
        if ele:
            return ele
    return None


def click_first(page, selectors, timeout=0.5):
    for sel in selectors:
        try:
            ele = page.ele(sel, timeout=timeout)
        except Exception:
            ele = None
        if ele:
            try:
                ele.click()
                return True
            except Exception:
                continue
    return False


def click_by_text(page, texts, timeout=0.5):
    for t in texts:
        selectors = [
            f"text:{t}",
            f"xpath://*[contains(., '{t}')]",
        ]
        for sel in selectors:
            try:
                ele = page.ele(sel, timeout=timeout)
            except Exception:
                ele = None
            if ele:
                try:
                    ele.click()
                    return True
                except Exception:
                    continue
    return False


def find_description_by_heading(page, headings, timeout=0.5):
    for h in headings:
        try:
            heading_ele = page.ele(f"xpath://*[normalize-space()='{h}']", timeout=timeout)
        except Exception:
            heading_ele = None
        if not heading_ele:
            try:
                heading_ele = page.ele(f"xpath://*[contains(normalize-space(), '{h}')]", timeout=timeout)
            except Exception:
                heading_ele = None
        if not heading_ele:
            continue
        # Try common structural relationships: next sibling or parent container.
        for rel in [
            "xpath:following-sibling::*[1]",
            "xpath:following::*[1]",
            "xpath:parent::*",
        ]:
            try:
                ele = heading_ele.ele(rel, timeout=timeout)
            except Exception:
                ele = None
            if ele:
                text = clean_text(ele.text)
                if text and len(text) > 20:
                    return text
    return ""


def extract_labeled_value(text, labels):
    if not text:
        return ""
    for label in labels:
        pattern = rf"(?:^|\n|\r)\s*{re.escape(label)}\s*[:\-]\s*(.+)"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # stop at next labeled line if present
            value = re.split(r"\n\s*[A-Za-z][A-Za-z /]{1,30}\s*[:\-]\s*", value)[0].strip()
            if value:
                return value
    return ""


def extract_salary(text):
    if not text:
        return ""
    # Common patterns: "$120,000", "£50k", "USD 80,000", "€70,000 - €90,000"
    currency = r"(?:\$|£|€|USD|GBP|EUR)"
    amount = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s?[kK])?"
    range_sep = r"(?:\s?[-–to]+\s?)"
    pattern = rf"{currency}\s*{amount}(?:{range_sep}{currency}?\s*{amount})?"
    match = re.search(pattern, text)
    if match:
        return match.group(0).strip()
    # Fallback: ranges without currency, e.g., "70,000 - 85,000" or "70k-85k"
    range_no_currency = rf"\b{amount}\s*[-to]+\s*{amount}\b"
    match = re.search(range_no_currency, text)
    return match.group(0).strip() if match else ""


def extract_location(text):
    if not text:
        return ""
    # Prefer explicit labels
    labeled = extract_labeled_value(text, ["Location", "Job location"])
    if labeled:
        return labeled
    # Common phrasing: "in London", "in Manchester", "based in London"
    match = re.search(r"\b(?:in|based in)\s+([A-Z][A-Za-z0-9 ,.'-/]{2,60})", text)
    if match:
        return match.group(1).strip()
    # Remote/hybrid keywords
    if re.search(r"\bremote\b", text, flags=re.IGNORECASE):
        if re.search(r"\bhybrid\b", text, flags=re.IGNORECASE):
            return "Hybrid"
        return "Remote"
    return ""


def extract_company(text):
    if not text:
        return ""
    labeled = extract_labeled_value(text, ["Company", "Employer"])
    if labeled:
        return labeled
    # Heuristic: "Company Background <Name> ..."
    match = re.search(r"\bCompany Background\s+([A-Z][A-Za-z0-9&' -]{2,60})", text)
    if match:
        return match.group(1).strip()
    # Heuristic: "About <Name>" (only if looks like a proper noun)
    match = re.search(r"\bAbout\s+([A-Z][A-Za-z0-9&' -]{2,60})\b", text)
    if match:
        return match.group(1).strip()
    return ""


def build_gjobs_url(query, location):
    q = quote_plus(f"{query} jobs {location}".strip())
    return f"https://www.google.com/search?q={q}&jbr=sep:0&udm=8"


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape Google Jobs listings.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Job title or keywords.")
    parser.add_argument(
        "--location",
        default=",".join(DEFAULT_LOCATIONS),
        help="Comma-separated job locations (e.g., london,birmingham).",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=0,
        help="Max jobs per location (0 = no limit).",
    )
    return parser.parse_args()


def parse_locations(raw_value):
    return [loc.strip() for loc in raw_value.split(",") if loc.strip()]


args = parse_args()
locations = parse_locations(args.location)
page = ChromiumPage()

# Open a CSV file to write the data
with open("google_jobs.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "Title",
        "Company",
        "Location",
        "Posted Time",
        "Job Link",
        "Description Snippet",
        "Description Full",
        "Salary",
    ])

    for location in locations:
        print(f"[google] location={location} url={build_gjobs_url(args.query, location)}", flush=True)
        page.get(build_gjobs_url(args.query, location))
        time.sleep(3)  # Wait for the page to load

        job_cards = page.eles("xpath://div[contains(@class,'GoEOPd')]")
        print(f"[google] location={location} cards={len(job_cards)}", flush=True)
        job_count = 0
        for job in job_cards:
            try:
                if args.max_jobs and job_count >= args.max_jobs:
                    print(f"[google] location={location} reached max_jobs={args.max_jobs}", flush=True)
                    break
                click_target = first_ele(job, ["xpath:.//*[contains(@class,'tNxQIb')]"], timeout=0.5)
                if click_target:
                    click_target.click()
                else:
                    job.click()
                time.sleep(0.2)

                title = safe_text(first_ele(job, ["xpath:./div", "xpath:.//div"], timeout=0.5))
                company = safe_text(first_ele(job, ["xpath:.//*[contains(@class,'waQ7qe')]"], timeout=0.5))
                location = safe_text(first_ele(job, ["xpath:.//*[contains(@class,'mLdNec')]"], timeout=0.5))
                posted_time = safe_text(first_ele(job, ["xpath:.//*[contains(@class,'RcZtZb')]"], timeout=0.5))
                job_link = safe_href(first_ele(job, ["xpath:.//a[@href]"], timeout=0.5))
                # Expand the panel description using simple text selector
                try:
                    page.ele("text:Show full description", timeout=1).click()
                except Exception:
                    pass  # Button might not exist or already expanded
                time.sleep(0.2)
                # Job details are usually in the right-side panel, not the card itself.
                desc_snippet = safe_text(first_ele(page, [".HBvzbc", ".K7O2sd", ".GYM22b"], timeout=0.5))
                desc_full = safe_text(first_ele(page, ["#jobDescriptionText", ".K7O2sd", ".HBvzbc"], timeout=0.5))
                if not desc_full:
                    desc_full = find_description_by_heading(
                        page,
                        ["Job description", "Description", "Responsibilities", "About the job"],
                        timeout=0.5,
                    )

                # Parse Company/Location/Salary from Description Full
                parsed_company = extract_company(desc_full)
                parsed_location = extract_location(desc_full)
                salary = extract_labeled_value(desc_full, ["Salary", "Compensation", "Pay"]) or extract_salary(desc_full)
                if parsed_company:
                    company = parsed_company
                if parsed_location:
                    location = parsed_location

                writer.writerow([
                    title,
                    company,
                    location,
                    posted_time,
                    job_link,
                    desc_snippet,
                    desc_full,
                    salary,
                ])
                job_count += 1

            except Exception as e:
                print(f"Error occurred: {e}")
                continue

# Close the DrissionPage
page.close()

print("Job data has been successfully saved to google_jobs.csv")
