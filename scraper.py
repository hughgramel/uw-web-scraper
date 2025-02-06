# Todo


# python3 -m venv venv
# ls -l venv/bin/activate
# source venv/bin/activate
# python --version
# pip install beautifulsoup4 requests
# python3 scraper.py


import re
import string
from tokenize import String
from bs4 import BeautifulSoup
import requests

page_to_scrape = requests.get("https://www.washington.edu/students/timeschd/SPR2025/cse.html")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# Find all tables with background color = "#ccffcc"
course_tables = soup.find_all("table", bgcolor="#ccffcc")

course_info = []  # we'll collect dictionaries of {code, name, credits} here



def is_nonwhite_bg(table):
    """
    Returns True if the table has a bgcolor attribute that is NOT "#ffffff" (case-insensitive).
    Returns False if it is "#ffffff" or if there's no bgcolor at all.
    """
    bg = table.get("bgcolor", "").strip().lower()  # e.g. "#ccffcc" -> "#ccffcc"
    # If bgcolor is missing or explicitly '#ffffff'
    if not bg or bg == "#ffffff":
        return False
    return True



def parse_course_tables(tables):
    """
    Given a list of tables (e.g., nonwhite tables),
    extract the course code, name, and credits from each.
    Returns a list of dicts like:
        {
            'code': 'CSE 121',
            'name': 'COMP PROGRAMMING I',
            'credits': '(NSc, RSN)'
        }
    """
    course_info = []
    

    curr_course_code = ""
    curr_course_name = ""
    curr_course_credits = ""
    curr_course_professor = ""
    for table in tables:
        # Typically each table has a single row (<tr>) with two <td> cells:
        #  1) Left <td>  -> "CSE 121" and "COMP PROGRAMMING I"
        #  2) Right <td> -> "(NSc, RSN)" (the credit type)
        
        if (is_nonwhite_bg(table)):
            rows = table.find_all("tr")
            if not rows:
                continue

            # The first (and often only) <tr> in the table
            cells = rows[0].find_all("td")
            if len(cells) < 2:
                # If fewer than 2 cells, skip
                continue

            left_cell = cells[0]
            right_cell = cells[1]

            # ---------------------
            # Extract "CSE 121" (course code)
            # Usually this text is inside <a name="cse123">…</a>
            # ---------------------
            code_anchor = left_cell.find("a", attrs={"name": True})
            if code_anchor:
                course_code = code_anchor.get_text(strip=True)
                course_code = " ".join(course_code.split())
            else:
                course_code = "Unknown Code"

            # ---------------------
            # Extract "COMP PROGRAMMING I" (course name)
            # Often in the same <td>, there's another <a> with an href containing 'cse.html#'
            # ---------------------
            all_anchors = left_cell.find_all("a", href=True)
            course_name = None
            for a in all_anchors:
                if "cse.html#" in a["href"]:
                    course_name = a.get_text(strip=True)
                    break
            if not course_name:
                course_name = "Unknown Name"

            # ---------------------
            # Extract credits, e.g. "(NSc, RSN)"
            # Usually in the second <td> there’s a <b> tag containing these designations.
            # ---------------------
            b_tag = right_cell.find("b")
            credits = b_tag.get_text(strip=True) if b_tag else "Unknown Credits"

            # Collect the course info

            curr_course_code = course_code
            curr_course_name = course_name
            curr_course_credits = curr_course_credits
            course_info.append({
                "code": course_code,
                "name": course_name,
                "credits": credits
            })
        else:
            print("Nonwhite: " + curr_course_code + " : " + curr_course_name + " : " + curr_course_credits)
            pre_tag = table.find("pre")
            if pre_tag:
                # Do something with the <pre> text
                # print("PRE tag contents:", pre_tag.get_text(strip=True))
                print(parse_pre_block(pre_tag))
            else:
                print("No <pre> found in this table.")

    return course_info


def parse_pre_block(pre_tag):
    """
    Example:
      <pre>
        <a href="...">12667</a>
        " A 4 WF 330-420 "
        <a href="...">KNE</a>
        " 120 Natsuhara,Miya Kaye Open 0/ 440 "
      </pre>

    Returns a dict:
      {
        'sln': '12667',
        'section_info': 'A 4 WF 330-420',
        'building': 'KNE',
        'rest_info': '120 Natsuhara,Miya Kaye Open 0/ 440'
      }
    """
    
    #BELOW PRINTS OUT FIRST CHILDREN OF PRE

    # children_list = list(pre_tag.children)
    
    # limited_children = children_list[:50]
    
    # print(f"Found {len(children_list)} total children. Showing up to 50:")
    # for i, child in enumerate(limited_children):
    #     print(f"{i}: {repr(child)}")

    children = list(pre_tag.children)  # convert the generator to a list

    result = {
        "enrollment_restriction": [],
        "sln": None,
        "section_info": None,
        "building": None,
        "extra_info": None
    }

    # --- Child 0: text node (restriction or empty) ---
    if len(children) > 0:
        child0_text = (children[0].string or "").strip()
        if child0_text:
            # Split on whitespace to get multiple tokens (e.g., ["IS", ">"])
            result["enrollment_restriction"] = child0_text.split()
        else:
            # No restriction
            result["enrollment_restriction"] = []

    # --- Child 1: <a> for SLN ---
    if len(children) > 1:
        child1 = children[1]
        if getattr(child1, "name", None) == "a":
            result["sln"] = child1.get_text(strip=True)
        else:
            result["sln"] = "No SLN found"

    # --- Child 2: text node => section info (e.g. " B 4 MWF 230-320 ") ---
    if len(children) > 2:
        child2 = children[2]
        if not getattr(child2, "name", None):
            result["section_info"] = (child2.string or "").strip()

    # --- Child 3: <a> => building code (e.g. "CSE2") ---
    if len(children) > 3:
        child3 = children[3]
        if getattr(child3, "name", None) == "a":
            result["building"] = child3.get_text(strip=True)

    # --- Child 4: text node => remainder info (room #, seats, TBA, etc.) ---
    if len(children) > 4:
        child4 = children[4]
        if not getattr(child4, "name", None):
            result["extra_info"] = (child4.string or "").strip()

    return result




if __name__ == "__main__":
    url = "https://www.washington.edu/students/timeschd/SPR2025/cse.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # 1) Get all tables
    all_tables = soup.find_all("table")

    # 2) Filter to only those with a nonwhite background

    # 3) Parse those tables for course info
    courses_found = parse_course_tables(all_tables)

    # 4) Print results
    for course in courses_found:
        print(f"{course['code']} - {course['name']} - {course['credits']}")