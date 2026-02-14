# Job Scraping Toolkit (DrissionPage)

Small scripts to scrape job listings from Google Jobs, Indeed, and Reed, then merge them into a single deduplicated CSV.

## What Is Here
- `google_s.py`
  Single-run Google Jobs scraper. Writes `google_jobs.csv`.
- `job_boards.py`
  Scrapes Indeed and Reed. Writes `jobs_indeed_reed.csv`.
- `merge_jobs.py`
  Merges all outputs and deduplicates into `jobs_all.csv`.
- `run_all.py`
  Runs Google + Indeed/Reed then merges into one file.

## Requirements
- Python 3.9+ (3.10+ recommended)
- Chromium installed or available to DrissionPage
- Packages in `requirements.txt`

## Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Start
```powershell
python run_all.py
```
Output: `jobs_all.csv`

## Usage
Google Jobs (single run):
```powershell
python google_s.py
```
Output: `google_jobs.csv`

Indeed + Reed:
```powershell
python job_boards.py
```
Output: `jobs_indeed_reed.csv`

Merge only:
```powershell
python merge_jobs.py
```
Output: `jobs_all.csv`

## Configure Searches
Pass search options as arguments:
```powershell
python run_all.py --query "AI developer" --location "london,birmingham,coventry,manchester" --max-pages 2
python google_s.py --query "AI developer" --location "london,birmingham"
python job_boards.py --query "AI developer" --location "london,birmingham,coventry,manchester" --max-pages 2
```

## Output Columns
`jobs_all.csv` columns:
- `Source`
- `Title`
- `Company`
- `Location`
- `Posted Time`
- `Job Link`
- `Description Snippet`
- `Description Full`
- `Collected At`

## Notes
- Google and job boards often block automated scraping. Expect CAPTCHA or missing results.
- Site HTML changes can break selectors; update them as needed.
- If results are empty, verify the URLs still show listings in your browser.

## Troubleshooting
- If Chromium fails to launch, confirm it is installed and on PATH or configured for DrissionPage.
