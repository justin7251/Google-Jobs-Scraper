from DrissionPage import ChromiumPage
import csv
import time
from urllib.parse import quote_plus

QUERY = "php developer"
LOCATION = "birmingham"
MAX_PAGES = 1  # Increase carefully; some sites block aggressive scraping

BOARDS = [
    {
        "name": "indeed",
        "base_url": "https://www.indeed.com",
        "search_url": "https://www.indeed.com/jobs?q={query}&l={location}&start={start}",
        "card_selectors": [".job_seen_beacon", ".result"],
        "selectors": {
            "title": ["h2.jobTitle", "a.jcs-JobTitle"],
            "company": ["span.companyName"],
            "location": ["div.companyLocation"],
            "posted_time": ["span.date"],
            "link": ["a.jcs-JobTitle"],
        },
    },
    {
        "name": "reed",
        "base_url": "https://www.reed.co.uk",
        "search_url": "https://www.reed.co.uk/jobs/{query}-jobs-in-{location}?p={page}",
        "card_selectors": ["article.job-result", "li.job-result"],
        "selectors": {
            "title": ["h2.job-result-heading__title", "h2.job-result__title"],
            "company": ["a.job-result-heading__company", "span.job-result__company"],
            "location": ["span.job-result-heading__location", "span.job-result__location"],
            "posted_time": ["span.job-result-heading__date", "span.job-result__date"],
            "link": ["a.job-result-heading__title", "a.job-result__title"],
        },
    },
]


def first_ele(parent, selectors):
    for sel in selectors:
        try:
            ele = parent.ele(sel)
        except Exception:
            ele = None
        if ele:
            return ele
    return None


def safe_text(ele):
    return ele.text if ele else ""


def safe_href(ele):
    return ele.attr("href") if ele else ""


def build_url(board, page_index):
    q = quote_plus(QUERY)
    loc = quote_plus(LOCATION)
    if board["name"] == "indeed":
        return board["search_url"].format(query=q, location=loc, start=page_index * 10)
    return board["search_url"].format(query=q, location=loc, page=page_index + 1)


def normalize_link(base_url, href):
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return f"{base_url}{href}"
    return f"{base_url}/{href}"


def scrape_board(page, board, writer):
    for page_index in range(MAX_PAGES):
        url = build_url(board, page_index)
        page.get(url)
        time.sleep(3)

        cards = page.eles(board["card_selectors"][0])
        if not cards and len(board["card_selectors"]) > 1:
            cards = page.eles(board["card_selectors"][1])

        for card in cards:
            title_ele = first_ele(card, board["selectors"]["title"])
            company_ele = first_ele(card, board["selectors"]["company"])
            location_ele = first_ele(card, board["selectors"]["location"])
            posted_ele = first_ele(card, board["selectors"]["posted_time"])
            link_ele = first_ele(card, board["selectors"]["link"])

            title = safe_text(title_ele)
            company = safe_text(company_ele)
            location = safe_text(location_ele)
            posted_time = safe_text(posted_ele)
            job_link = normalize_link(board["base_url"], safe_href(link_ele))

            writer.writerow([
                board["name"],
                title,
                company,
                location,
                posted_time,
                job_link,
            ])


def main():
    page = ChromiumPage()

    with open("jobs_indeed_reed.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Title", "Company", "Location", "Posted Time", "Job Link"])

        for board in BOARDS:
            scrape_board(page, board, writer)

    page.close()
    print("Job data has been successfully saved to jobs_indeed_reed.csv")


if __name__ == "__main__":
    main()
