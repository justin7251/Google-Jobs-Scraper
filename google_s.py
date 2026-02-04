from DrissionPage import ChromiumPage
import argparse
import csv
import time
from urllib.parse import quote_plus

DEFAULT_QUERY = "php developer"
DEFAULT_LOCATIONS = ["london", "birmingham", "coventry", "manchester"]


def safe_text(ele):
    return ele.text if ele else ""


def safe_href(ele):
    return ele.attr("href") if ele else ""


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
    return parser.parse_args()


def parse_locations(raw_value):
    return [loc.strip() for loc in raw_value.split(",") if loc.strip()]


args = parse_args()
locations = parse_locations(args.location)
page = ChromiumPage()

# Open a CSV file to write the data
with open("google_jobs.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Company", "Location", "Posted Time", "Job Link"])

    for location in locations:
        page.get(build_gjobs_url(args.query, location))
        time.sleep(3)  # Wait for the page to load

        job_cards = page.eles(".GoEOPd")
        for job in job_cards:
            try:
                job.click(".tNxQIb")
                time.sleep(0.2)

                title = safe_text(job.ele("css:>div"))
                company = safe_text(job.ele("@class:waQ7qe"))
                location = safe_text(job.ele("@class:mLdNec"))
                posted_time = safe_text(job.ele("@class:RcZtZb"))
                job_link = safe_href(job.ele("a[href]"))

                writer.writerow([title, company, location, posted_time, job_link])

            except Exception as e:
                print(f"Error occurred: {e}")
                continue

# Close the DrissionPage
page.close()

print("Job data has been successfully saved to google_jobs.csv")
