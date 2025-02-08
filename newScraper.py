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

def print_in_json_format(data):
    """
    Takes a Python object (list/dict) and prints it in pretty JSON format.
    """
    print(json.dumps(data, indent=2))

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


def get_background_color(season):
    """This function returns the correct background color of the course row
    headers based on the season.
    

    Args:
        season (string): Season to base the bg color off of
    """

    if season == "SPR":
        return  "#ccffcc"
    elif season == "AUT":
        return  "#ffcccc"
    elif season == "WIN":
        return  "#99ccff"
    else:
        return  #ffffcc


def traverse_schedule_page(page, season):
    """ This method goes through a page and returns a record with all of the courses
    indicated.

    Args:
        page (string): The page to be traversed
        season (string): the quarters seasons
        https://www.washington.edu/students/timeschd/
    """

    allCourses = []
    # For this we want to take all courses, and add records of each course to this
    
    curr_course_code = ""
    curr_course_name = ""
    curr_course_fulfills = ""


    bg_color = get_background_color(season)

    page_to_scrape = requests.get(page)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    course_tables = soup.find_all("table")
    for table in course_tables:
        # print(table)

        if table.get("bgcolor") and table.get("bgcolor") == bg_color:
            all_anchors = table.find_all("a")

            # Here we reset them all because we know they'll be reassigned
            curr_course_code = ""
            curr_course_name = ""
            curr_course_fulfills = ""

            # Then we get the code, name, and credits it fullfills
            curr_course_code = " ".join(str(all_anchors[0].string).strip().split())
            curr_course_name = all_anchors[1].string

            # Only make the current fullfill if it exists. Otherwise nothing
            fulfills = table.find_all("b")[1].string
            if fulfills:
                curr_course_fulfills = fulfills[1:-1].split(",")

            # Actually rethinking this, we should only make the record
            # if we're on the other tables.
            record = {}
            record["curr_course_code"] = curr_course_code
            record["curr_course_name"] = curr_course_name
            record["curr_course_fulfills"] = curr_course_fulfills
            
            allCourses.append(record)
        elif curr_course_code and curr_course_name:
            print(curr_course_code)
            next_pre = table.find("pre")
            text = next_pre.get_text()
            # print(next_pre)
            print(text)
    return allCourses

base = "https://www.washington.edu/students/timeschd/SPR2025/"
pages = [base + "meche.html"]
# pages = [base + "cse.html", base + "meche.html", base + "envst.html"]
for page in pages:
    record_of_all_courses = traverse_schedule_page(page, "SPR")
    # print_in_json_format(record_of_all_courses)


