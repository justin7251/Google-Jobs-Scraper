from DrissionPage import ChromiumPage
import csv
import time

# Google Jobs search URL
GJOBS_URL = "https://www.google.com/search?q=php%20developer%20jobs%20birmingham&jbr=sep:0&udm=8&ved=2ahUKEwjHp9regJaIAxUnTkEAHWHTAUgQ3L8LegQIMhAM"


def safe_text(ele):
    return ele.text if ele else ""


def safe_href(ele):
    return ele.attr("href") if ele else ""


# Initialize Drission and ChromiumPage
page = ChromiumPage()

# Open the Google Jobs page
page.get(GJOBS_URL)
time.sleep(3)  # Wait for the page to load

# Open a CSV file to write the data
with open("google_jobs.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Company", "Location", "Posted Time", "Job Link"])

    # Extract job listings
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

            # Write job details to CSV
            writer.writerow([title, company, location, posted_time, job_link])

        except Exception as e:
            print(f"Error occurred: {e}")
            continue

# Close the DrissionPage
page.close()

print("Job data has been successfully saved to google_jobs.csv")
