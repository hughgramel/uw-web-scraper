# Todo


# python3 -m venv venv
# ls -l venv/bin/activate
# source venv/bin/activate
# python --version
# pip install beautifulsoup4 requests
# python3 scraper.py


from bs4 import BeautifulSoup
import requests

page_to_scrape = requests.get("https://www.washington.edu/students/timeschd/SPR2025/cse.html")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")
print(soup)
