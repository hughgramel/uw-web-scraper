# Todo


# python3 -m venv venv
# ls -l venv/bin/activate
# source venv/bin/activate
# python --version
# pip install beautifulsoup4 requests
# python3 scraper.py


import re
import json
import string
from tokenize import String
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin


prefixes = ["cse", "meche", "BMW"]
# Try it Yourself »
page_to_scrape = requests.get("https://www.washington.edu/students/timeschd/SPR2025/cse.html")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

POSSIBLE_SEASONS = ["AUT, ""WIN", "SPR", "SUM"]
seasons = ["SPR"]
years = ["2025"]



def gather_all_prefixes(season, year):
    """
        This method goes through the entire page of the given season / year
        combination of the UW's course offerings. If they don't exist, throws
        exception. Returns an array with all possible PREFIXES for that year
    """
    link_array = []
    if (season not in POSSIBLE_SEASONS):
        raise Exception("Season not valid")
    base = "https://www.washington.edu/students/timeschd/" + season + year
    page_to_scrape = requests.get(base)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    course_tables = soup.find_all("a")
    for course in course_tables:
        course_code = course.string
        if (course_code and "(" in course_code and ")" in course_code):
            link_array.append(urljoin(base, course.get("href")))
        # This above is the code
    return link_array


def traverse_schedule_page(page):
    """ This method goes through a page and adds to a record all of the courses
    indicated.

    Args:
        arr (string[]): The array of links to be traversed, must be prefaced by 
        https://www.washington.edu/students/timeschd/
    """
    page_to_scrape = requests.get(page)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    course_tables = soup.find_all("table")
    for table in course_tables:
        # print(table)
        rows = table.find_all("tr")
        for row in rows:
            print(row)

    
    
    
base = "https://www.washington.edu/students/timeschd/SPR2025/"
# pages = [base + "cse.html", base + "meche.html", base + "envst.html"]
pages = [base + "cse.html"]
for page in pages:
    traverse_schedule_page(page)


