#!/usr/bin/env python3
"""
UW Course Scraper

A Python script to scrape course offerings from the University of Washington's
time schedule website and save them as structured JSON data.

Usage:
    python3 uw_course_scraper.py [options]

Options:
    --season SEASON    Season to scrape (AUT, WIN, SPR, SUM) [default: SPR]
    --year YEAR        Year to scrape [default: 2025]
    --department DEPT  Specific department to scrape (e.g., cse, math, phys)
    --all              Scrape all departments
    --output-dir DIR   Output directory for results [default: course_offerings]
    --help             Show this help message

Examples:
    # Scrape CSE courses for Spring 2025
    python3 uw_course_scraper.py --department cse

    # Scrape all departments for Winter 2025
    python3 uw_course_scraper.py --all --season WIN --year 2025

    # Scrape Math courses and save to custom directory
    python3 uw_course_scraper.py --department math --output-dir my_courses
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class UWCourseScraper:
    """Main scraper class for UW course offerings."""
    
    POSSIBLE_SEASONS = ["AUT", "WIN", "SPR", "SUM"]
    BASE_URL = "https://www.washington.edu/students/timeschd/"
    
    def __init__(self, season="SPR", year="2025", output_dir="course_offerings"):
        """Initialize the scraper with season, year, and output directory."""
        self.season = season.upper()
        self.year = year
        self.output_dir = output_dir
        
        if self.season not in self.POSSIBLE_SEASONS:
            raise ValueError(f"Invalid season: {season}. Must be one of {self.POSSIBLE_SEASONS}")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_background_color(self):
        """Get the background color for course headers based on season."""
        colors = {
            "SPR": "#ccffcc",
            "AUT": "#ffcccc", 
            "WIN": "#99ccff",
            "SUM": "#ffffcc"
        }
        return colors.get(self.season, "#ffffcc")
    
    def matches_weekday(self, s):
        """Check if string contains only weekday codes."""
        codes = "MThWFS"
        return all(char in codes for char in s)
    
    def matches_other_code(self, s):
        """Check if string contains only other codes."""
        codes = "ABOEHJRSW%#"
        return all(char in codes for char in s)
    
    def gather_all_departments(self):
        """Get all available department links for the given season/year."""
        base_url = f"{self.BASE_URL}{self.season}{self.year}/"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching department list: {e}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        
        for link in soup.find_all("a"):
            if link.string and "(" in link.string and ")" in link.string:
                dept_name = link.get("href", "").replace(".html", "")
                if dept_name:
                    links.append({
                        "name": dept_name,
                        "url": base_url + link.get("href")
                    })
        
        return links
    
    def scrape_department(self, department_url, department_name):
        """Scrape course data from a specific department page."""
        print(f"Scraping {department_name}...")
        
        try:
            response = requests.get(department_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {department_name}: {e}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        courses = []
        
        curr_course_code = ""
        curr_course_name = ""
        curr_course_fulfills = ""
        bg_color = self.get_background_color()
        
        tables = soup.find_all("table")
        for table in tables:
            if table.get("bgcolor") == bg_color:
                # This is a course header
                anchors = table.find_all("a")
                if len(anchors) >= 2:
                    curr_course_code = " ".join(str(anchors[0].string).strip().split())
                    curr_course_name = anchors[1].string
                    
                    # Get fulfillment requirements
                    bold_tags = table.find_all("b")
                    if len(bold_tags) > 1 and bold_tags[1].string:
                        fulfills = bold_tags[1].string[1:-1].split(",")
                        curr_course_fulfills = [f.strip() for f in fulfills]
                    else:
                        curr_course_fulfills = []
            
            elif curr_course_code and curr_course_name:
                # This is a course section
                course_data = self._parse_course_section(table, curr_course_code, 
                                                       curr_course_name, curr_course_fulfills)
                if course_data:
                    courses.append(course_data)
        
        return courses
    
    def _parse_course_section(self, table, course_code, course_name, course_fulfills):
        """Parse individual course section data from a table."""
        pre_tag = table.find("pre")
        if not pre_tag:
            return None
        
        text = pre_tag.get_text()
        lines = text.splitlines()[1:]  # Skip first line
        
        if not lines:
            return None
        
        # Initialize course record
        record = {
            "restrictions": [],
            "add_code": "",
            "section": "",
            "is_quiz": False,
            "is_lab": False,
            "credits": "0",
            "credits_vary": False,
            "class_times": [],
            "c/nc": False,
            "course_fee": "0",
            "other_codes": "",
            "is_estimate": False,
            "max_capacity": "0",
            "curr_enrolled": "0",
            "open_or_closed": "",
            "professor_name": "",
            "curr_course_code": course_code,
            "curr_course_name": course_name.strip(),
            "curr_course_fulfills": course_fulfills
        }
        
        # Parse first line
        first_line = lines[0]
        
        # Restrictions (first 7 characters)
        restrictions = first_line[:7].strip()
        record["restrictions"] = restrictions.split() if restrictions else []
        
        # Add code (next 5 characters)
        remaining = first_line[7:]
        record["add_code"] = remaining[:5].strip()
        
        # Parse the rest of the line
        remaining = remaining[6:].split()
        if not remaining:
            return record
        
        record["section"] = remaining[0]
        
        # Credits or section type
        if len(remaining) > 1:
            first = remaining[1]
            if first == "QZ":
                record["is_quiz"] = True
            elif first == "LB":
                record["is_lab"] = True
            elif first == "VAR":
                record["credits"] = "VAR"
            elif first == "SM":
                record["credits"] = "0"
            elif "-" in first:
                record["credits"] = first
                record["credits_vary"] = True
            else:
                record["credits"] = first
        
        # Parse class times and other data
        self._parse_class_times_and_details(remaining[2:], record)
        
        # Parse additional lines for more class times
        if len(lines) > 1:
            self._parse_additional_class_times(lines[1], record)
        
        return record
    
    def _parse_class_times_and_details(self, remaining, record):
        """Parse class times and other course details."""
        if not remaining:
            return
        
        # Handle "to be arranged" case
        if remaining[0] == "to":
            remaining = remaining[3:]
        else:
            # Parse class time
            if len(remaining) >= 4:
                event = {
                    "days": remaining[0],
                    "time": remaining[1],
                    "building": remaining[2] if remaining[2] != "*" else "TBA",
                    "room": remaining[3] if remaining[3] != "*" else "TBA"
                }
                record["class_times"].append(event)
                remaining = remaining[4:]
        
        # Parse remaining details (professor, enrollment, etc.)
        self._parse_enrollment_details(remaining, record)
    
    def _parse_enrollment_details(self, remaining, record):
        """Parse enrollment and professor details."""
        if not remaining:
            return
        
        # Check for CR/NC, course fees, etc.
        last = remaining[-1]
        if last == "CR/NC":
            record["c/nc"] = True
            remaining = remaining[:-1]
        elif "$" in last:
            record["course_fee"] = last
            remaining = remaining[:-1]
        elif self.matches_other_code(last):
            record["other_codes"] = last
            remaining = remaining[:-1]
        elif "E" in last:
            record["is_estimate"] = True
            record["max_capacity"] = last[:-1]
            remaining = remaining[:-1]
        else:
            record["max_capacity"] = last
            remaining = remaining[:-1]
        
        # Parse enrollment status and professor
        if remaining:
            last = remaining[-1]
            if "/" in last:
                record["curr_enrolled"] = last.split("/")[0]
                remaining = remaining[:-1]
            elif last in ["Open", "Closed"]:
                record["open_or_closed"] = last
                remaining = remaining[:-1]
        
        # Get professor name
        if remaining:
            record["professor_name"] = " ".join(remaining)
    
    def _parse_additional_class_times(self, line, record):
        """Parse additional class times from subsequent lines."""
        parts = line.split()
        if (len(parts) >= 2 and 
            self.matches_weekday(parts[0]) and 
            parts[1][0].isdigit()):
            
            event = {
                "days": parts[0],
                "time": parts[1],
                "building": "TBA",
                "room": "TBA"
            }
            
            # Use building/room from first class time if available
            if record["class_times"]:
                first_class = record["class_times"][0]
                event["building"] = first_class["building"]
                event["room"] = first_class["room"]
            
            record["class_times"].append(event)
    
    def convert_to_structured_format(self, courses):
        """Convert flat course list to structured format with main courses, labs, and quizzes."""
        structured = {}
        
        for course in courses:
            course_code = course["curr_course_code"]
            section = course["section"]
            
            # Create course entry if it doesn't exist
            if course_code not in structured:
                structured[course_code] = {}
            
            # Determine if this is a main section, lab, or quiz
            if (len(section) == 1 or 
                (len(section) == 2 and section[1].isdigit() and 
                 not course["is_quiz"] and not course["is_lab"])):
                # Main section
                section_key = f"{course_code}{section}"
                structured[course_code][section_key] = {
                    "main_course": course
                }
            else:
                # Lab or quiz section
                main_section = section[0]
                main_key = f"{course_code}{main_section}"
                
                if main_key in structured[course_code]:
                    if course["is_quiz"]:
                        if "quiz_list" not in structured[course_code][main_key]:
                            structured[course_code][main_key]["quiz_list"] = []
                        structured[course_code][main_key]["quiz_list"].append(course)
                    elif course["is_lab"]:
                        if "lab_list" not in structured[course_code][main_key]:
                            structured[course_code][main_key]["lab_list"] = []
                        structured[course_code][main_key]["lab_list"].append(course)
                    else:
                        if "other" not in structured[course_code][main_key]:
                            structured[course_code][main_key]["other"] = []
                        structured[course_code][main_key]["other"].append(course)
        
        return structured
    
    def save_courses(self, courses, department_name):
        """Save courses to JSON file."""
        structured_courses = self.convert_to_structured_format(courses)
        
        filename = f"{department_name}_course_offerings_{self.season}_{self.year}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(structured_courses, f, indent=2)
        
        print(f"Saved {len(courses)} courses to {filepath}")
        return filepath
    
    def scrape_single_department(self, department):
        """Scrape a single department."""
        url = f"{self.BASE_URL}{self.season}{self.year}/{department}.html"
        courses = self.scrape_department(url, department)
        if courses:
            return self.save_courses(courses, department)
        return None
    
    def scrape_all_departments(self):
        """Scrape all available departments."""
        departments = self.gather_all_departments()
        if not departments:
            print("No departments found!")
            return []
        
        print(f"Found {len(departments)} departments")
        results = []
        
        for dept in departments:
            courses = self.scrape_department(dept["url"], dept["name"])
            if courses:
                filepath = self.save_courses(courses, dept["name"])
                results.append(filepath)
        
        return results


def main():
    """Main function to handle command line arguments and run the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape UW course offerings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--season", default="SPR", 
                       choices=["AUT", "WIN", "SPR", "SUM"],
                       help="Season to scrape (default: SPR)")
    parser.add_argument("--year", default="2025", 
                       help="Year to scrape (default: 2025)")
    parser.add_argument("--department", 
                       help="Specific department to scrape (e.g., cse, math, phys)")
    parser.add_argument("--all", action="store_true",
                       help="Scrape all departments")
    parser.add_argument("--output-dir", default="course_offerings",
                       help="Output directory for results (default: course_offerings)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.department and not args.all:
        print("Error: Must specify either --department or --all")
        parser.print_help()
        sys.exit(1)
    
    try:
        scraper = UWCourseScraper(
            season=args.season,
            year=args.year,
            output_dir=args.output_dir
        )
        
        print(f"UW Course Scraper - {args.season} {args.year}")
        print(f"Output directory: {args.output_dir}")
        print("-" * 50)
        
        if args.department:
            result = scraper.scrape_single_department(args.department)
            if result:
                print(f"\nSuccessfully scraped {args.department} courses!")
            else:
                print(f"\nNo courses found for {args.department}")
        else:
            results = scraper.scrape_all_departments()
            print(f"\nSuccessfully scraped {len(results)} departments!")
            print("Files created:")
            for result in results:
                print(f"  - {result}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
