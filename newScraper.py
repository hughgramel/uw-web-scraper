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

POSSIBLE_SEASONS = ["AUT", "WIN", "SPR", "SUM"]
seasons = ["SPR", "WIN"]
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
    base = "https://www.washington.edu/students/timeschd/" + season + year + "/"
    page_to_scrape = requests.get(base)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    course_tables = soup.find_all("a")
    for course in course_tables:
        course_code = course.string
        if (course_code and "(" in course_code and ")" in course_code):
            link_array.append(base + course.get("href"))
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

def matches_weekday(s):
    """This goes through each character and checks if they match an other code 

    Args:
        string (string): String to be checked
    """
    codes = "MThWFS"
    for char in s:
        if char not in codes:
            return 0
    return 1

def matches_other_code(s):
    """This goes through each character and checks if they match an other code 

    Args:
        string (string): String to be checked
    """
    codes = "ABOEHJRSW%#"
    for char in s:
        if char not in codes:
            return 0
    return 1    

    
    
    
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
        elif curr_course_code and curr_course_name:
            record = {}

            next_pre = table.find("pre")
            text = next_pre.get_text()
            all_lines = text.splitlines()[1:]
            n = 1
            # for line in all_lines:
            #     n+=1
            
            # First we get the restrictions from the first 7 characters
            # We make them just an array
            first_line = all_lines[0]
            restrictions = first_line[:7]
            record["restrictions"] = restrictions.split()

            # Now we get the add code
            # Like "13010 S  1-3     W      130-220    *    *                                   Open      0/  35  CR/NC"
            remaining_line = first_line[7:]
            add_code = remaining_line[:5]
            record["add_code"] = add_code
            
            # Now we go to the next 6 characters
            # We do 6 to remove the whitespace
            remaining_line = remaining_line[6:]
            split = remaining_line.split()
            section = split[0]
            record["section"] = section
            
            remaining = split[1:]
            first = remaining[0]
            # Now we have two scenarios. Either It's a credit count / range /
            # VAR OR it's a QZ / LB. Either way we add the data then go to the
            # next one
            record["isQuiz"] = "0"
            record["isLab"] = "0"
            record["credits"] = "0"
            record["credits_vary"] = "0"
            
            if first == "QZ":
                record["isQuiz"] = "1"
            elif first == "LB":
                record["isLab"] = "1"
            elif first == "VAR":
                record["credits"] = "VAR"
            elif first == "SM":
                record["credits"] = "0"
            elif "-" in first:
                record["credits"] = first
                record["credits_vary"] = "1"
            else:
                record["credits"] = first
            remaining = remaining[1:]
            
            first = remaining[0]
            record["class_times"] = []
            if first == "to":
                remaining = remaining[3:]
                
            else:
                event = {}
                event["days"] = remaining[0]
                event["time"] = remaining[1]
                
                event["building"] = remaining[2]
                event["room"] = remaining[3]
                if remaining[3] == "*":
                    event["building"] = "TBA"
                    event["room"] = "TBA"
                remaining = remaining[4:]
                record["class_times"].append(event)

            # Now we have two alternatives:
            # ['WF', '230-320', 'MGH', '288', 'Emigh,Charlotte', '0/', '25', 'CR/NC']
            # ['to', 'be', 'arranged', 'Dillon,Cade', '0/', '60', 'CR/NC']
            # So either "to" is first and we want to set remaining to [3:]
            # or it's a dates  / time / location
            
            record["c/nc"] = 0
            record["course_fee"] = "0"
            record["other_codes"] = ""
            record["is_estimate"] = 0
            record["max_capacity"] = "0"
            record["curr_enrolled"] = 0
            last = remaining[len(remaining) - 1]
            
            if last == "CR/NC":
                record["c/nc"] = 1
            elif "$" in last:
                record["course_fee"] = last
            elif matches_other_code(last):
                record["other_codes"] = last
            elif "E" in last:
                record["is_estimate"] = 1
                record["max_capacity"] = last[:-1]
            else:
                record["max_capacity"] = last
            remaining = remaining[:-1]
            last = remaining[len(remaining) - 1]
            #check again if cr/nc
            if last == "CR/NC":
                record["c/nc"] = 1
                remaining = remaining[:-1]
                if len(remaining) > 0:
                    last = remaining[len(remaining) - 1]

            record["curr_enrolled"] = "0"
            if "/" in last:
                record["curr_enrolled"] = last[:-1]
            elif "E" in last:
                record["is_estimate"] = 1
                record["max_capacity"] = last[:-1]
            elif "$" in last:
                record["course_fee"] = last
            else:
                record["max_capacity"] = last
            remaining = remaining[:-1]

            #check again if cr/nc
            if len(remaining) > 0 and remaining[len(remaining) - 1] == "CR/NC":
                record["c/nc"] = 1
                remaining = remaining[:-1]
            if len(remaining) > 0:
                if remaining[0] == "Open" or remaining[0] == "Closed":
                    record["open_or_closed"] = remaining[0]
                    remaining = remaining[1:]
                elif remaining[len(remaining) - 1] == "Open" or remaining[len(remaining) - 1] == "Closed":
                    record["open_or_closed"] = remaining[len(remaining) - 1]
                    remaining = remaining[:-1]
            if len(remaining) > 0:
                last = remaining[len(remaining) - 1]
                if "/" in last:
                    record["curr_enrolled"] = last[:-1]
                elif "," in last:
                    record["professor_name"] = last
                remaining = remaining[:-1]
            # if len(remaining) > 0:
            if (len(remaining) > 0):
                last = remaining[len(remaining) - 1]
                if last == "Open" or last == "Closed":
                    record["open_or_closed"] = last
                    remaining = remaining[:-1]
                if remaining[0] == "*" and len(remaining) > 1 and remaining[1] == "*":
                    remaining = remaining[2:]
                elif remaining[0] == "*":
                    remaining = remaining[1:]
            if "/" in last:
                record["curr_enrolled"] = last[:-1]
                remaining = remaining[:-1]
            if (len(remaining) > 0):
                last = remaining[len(remaining) - 1]
                if last == "Open" or last == "Closed":
                    record["curr_enrolled"] = last[:-1]
                    record["open_or_closed"] = last
                    remaining = remaining[:-1]
                record["professor_name"] = " ".join(remaining)
            
            if len(all_lines) > 1:
                split = all_lines[1].split()
                if matches_weekday(split[0]) and split[1][0] in "0123456789":
                    event = {}
                    event["days"] = split[0]
                    event["time"] = split[1]
                    if len(split) == 2 and len(record["class_times"]) > 0 and record["class_times"][0] and record["class_times"][0]["building"] and record["class_times"][0]["room"]:
                        if record["class_times"][0]["building"] and record["class_times"][0]["room"]:
                            event["building"] = record["class_times"][0]["building"]
                            event["room"] = record["class_times"][0]["room"]
                        elif split[2] == "*":
                            event["building"] = "TBA"
                            event["room"] = "TBA"   
                        else:
                            event["building"] = split[2]
                            event["room"] = split[3]
                    record["class_times"].append(event)
                # Then add to 

            # if len(remaining) > 1:
            # Now two possibilities are that we have already gotten the max OR
            # we haven't
            
            record["curr_course_code"] = curr_course_code
            record["curr_course_name"] = curr_course_name.strip()
            record["curr_course_fulfills"] = curr_course_fulfills
            
            allCourses.append(record)
            


    return allCourses

season = "SPR"
year = "2025"

base = "https://www.washington.edu/students/timeschd/" + season + year + "/"
# pages = [base + "cse.html"]
# pages = [base + "88aerosci.html"]
pages = gather_all_prefixes(season, year)
n = 0
record = {}
for page in pages:
    # n += 1
    
    record_of_all_courses = traverse_schedule_page(page, season)
    s = page.split("/")[-1:][0].split(".")[0]
    if s not in record:
        n += len(record_of_all_courses)
    # print(s + ": " + str(len(record_of_all_courses)))
    
    record[s] = len(record_of_all_courses)
    # print_in_json_format(record_of_all_courses)
    name = "./course_offerings_spr_25/" +  s + "_course_offerings_" + season + "_" + year
    json_object = json.dumps(record_of_all_courses, indent=4)
    with open(name, "w") as outfile:
        outfile.write(json_object)
# sorted_dict = {key: value for key,
#                value in sorted(record.items(),
#                                key=lambda item: item[1])}

# print_in_json_format(sorted_dict)
# print("Total: " + str(n))