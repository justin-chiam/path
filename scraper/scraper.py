# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "beautifulsoup4>=4.15.0",
#     "requests>=2.34.2",
# ]
# ///
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
import argparse
import json
import re
import sys
import requests
from bs4 import BeautifulSoup

YEAR = date.today().year
TIMETABLE_BASE = f"https://timetable.unsw.edu.au/{YEAR}"
TIMETABLE = TIMETABLE_BASE + "/subjectSearch.html"
SUBJECT_CODE_PATTERN = r"[A-Z]{4}"
COURSE_CODE_PATTERN = r"[A-Z]{4}\d{4}"
# Summary rows on a course page link to class details, e.g. "#S1-9904"
CLASS_ANCHOR_PATTERN = r"#[A-Z0-9]+-\d+"

session = requests.Session()


@dataclass
class Course:
    code: str
    title: str
    uoc: int
    terms: list[str] = field(default_factory=list)


def fetch_soup(url):
    """Fetch a page from a URL and return BeautifulSoup."""
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_subject_area_urls():
    """Scrape subject area page URLs from the main timetable page."""
    soup = fetch_soup(TIMETABLE)
    urls = []

    # Useful rows contain: subject code (with link), subject name, "offered by" text
    for row in soup.find_all("tr"):
        if len(row.find_all("td")) < 3:
            continue

        link = row.find("a", href=True)
        if not link:
            continue

        code = clean_text(link.get_text(" ", strip=True))
        if not re.fullmatch(SUBJECT_CODE_PATTERN, code):
            continue

        href = link["href"]
        if ".html" not in href:
            continue

        url = TIMETABLE_BASE + "/" + href
        if url not in urls:
            urls.append(url)

    return urls


def extract_courses(subject_url):
    """Scrape every course listed on a subject area page, across all careers."""
    soup = fetch_soup(subject_url)
    courses = []

    for row in soup.find_all("tr"):
        cells = [
            clean_text(cell.get_text(" ", strip=True)) for cell in row.find_all("td")
        ]
        if len(cells) < 3:
            continue

        links = row.find_all("a", href=True)
        if not links:
            continue

        code = clean_text(links[0].get_text(" ", strip=True))
        if not re.fullmatch(COURSE_CODE_PATTERN, code):
            continue

        title = (
            clean_text(links[1].get_text(" ", strip=True))
            if len(links) > 1
            else cells[1]
        )
        uoc = cells[-1]
        if not re.fullmatch(r"\d+", uoc):
            continue

        courses.append(Course(code=code, title=title, uoc=int(uoc)))

    return courses


def extract_terms(course_code):
    """Return the teaching periods (e.g. T1, T2) a course is offered in."""
    try:
        soup = fetch_soup(f"{TIMETABLE_BASE}/{course_code}.html")
    except requests.RequestException as e:
        print(f"  warning: no terms for {course_code}: {e}", file=sys.stderr)
        return []

    terms = []

    # Each class summary row is: activity, term, class number, section
    for row in soup.find_all("tr"):
        links = row.find_all("a", href=True)
        if len(links) < 2:
            continue
        if not all(re.fullmatch(CLASS_ANCHOR_PATTERN, link["href"]) for link in links):
            continue

        term = clean_text(links[1].get_text(" ", strip=True))
        if term and term not in terms:
            terms.append(term)

    return terms


def scrape_all(workers):
    print("Loading subject areas...", file=sys.stderr)
    subject_urls = extract_subject_area_urls()
    if not subject_urls:
        raise RuntimeError("No subject areas found. Timetable page may have changed.")

    courses = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        print(f"Loading courses from {len(subject_urls)} subject areas...", file=sys.stderr)
        for subject_courses in pool.map(extract_courses, subject_urls):
            for course in subject_courses:
                courses.setdefault(course.code, course)

        print(f"Loading terms for {len(courses)} courses...", file=sys.stderr)
        ordered = sorted(courses.values(), key=lambda course: course.code)
        codes = [course.code for course in ordered]
        for i, (course, terms) in enumerate(
            zip(ordered, pool.map(extract_terms, codes)), start=1
        ):
            course.terms = terms
            if i % 250 == 0:
                print(f"  {i}/{len(ordered)}", file=sys.stderr)

    return ordered


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dump UNSW courses from the timetable to JSON."
    )
    parser.add_argument(
        "--dump",
        required=True,
        type=Path,
        help="path to write the JSON output, e.g. ../data/courses.json.",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=8,
        help="number of concurrent requests (default: 8).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    courses = scrape_all(args.workers)

    args.dump.parent.mkdir(parents=True, exist_ok=True)
    with args.dump.open("w", encoding="utf-8") as f:
        json.dump([asdict(course) for course in courses], f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(courses)} courses to {args.dump}", file=sys.stderr)


if __name__ == "__main__":
    main()
