import argparse
import datetime
import time
from urllib.parse import quote_plus
from DrissionPage import ChromiumPage
from DataRecorder import Recorder

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
    parser = argparse.ArgumentParser(description="Scrape Google Jobs (threaded).")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Job title or keywords.")
    parser.add_argument(
        "--location",
        default=",".join(DEFAULT_LOCATIONS),
        help="Comma-separated job locations (e.g., london,birmingham).",
    )
    return parser.parse_args()


def parse_locations(raw_value):
    return [loc.strip() for loc in raw_value.split(",") if loc.strip()]


def collect(page, recorder, title):
    # One pass over current job cards
    job_cards = page.eles(".GoEOPd")
    num = 1
    for job in job_cards:
        try:
            job.click(".tNxQIb")
            time.sleep(0.2)

            job_title = safe_text(job.ele("css:>div"))
            company = safe_text(job.ele("@class:waQ7qe"))
            location = safe_text(job.ele("@class:mLdNec"))
            posted_time = safe_text(job.ele("@class:RcZtZb"))
            job_link = safe_href(job.ele("a[href]"))

            recorder.add_data((title, num, job_title, company, location, posted_time, job_link))
            num += 1

        except Exception:
            continue

    recorder.record()


def main():
    args = parse_args()
    locations = parse_locations(args.location)
    page = ChromiumPage()
    recorder = Recorder(f"data_{datetime.datetime.now():%d-%b-%Y}.csv")

    for location in locations:
        page.get(build_gjobs_url(args.query, location))
        time.sleep(3)
        collect(page, recorder, "job")


if __name__ == "__main__":
    main()
