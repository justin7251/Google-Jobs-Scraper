import datetime
import time
from threading import Thread
from DrissionPage import ChromiumPage
from DataRecorder import Recorder

GJOBS_URL = "https://www.google.com/search?q=php%20developer%20jobs%20birmingham&jbr=sep:0&udm=8&ved=2ahUKEwidv-yJ-JWIAxWkT0EAHSmbKnIQ3L8LegQIJBAM"


def safe_text(ele):
    return ele.text if ele else ""


def safe_href(ele):
    return ele.attr("href") if ele else ""


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
    page = ChromiumPage()
    page.get(GJOBS_URL)
    time.sleep(3)

    recorder = Recorder(f"data_{datetime.datetime.now():%d-%b-%Y}.csv")

    Thread(target=collect, args=(page, recorder, "job")).start()


if __name__ == "__main__":
    main()
