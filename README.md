# UW Course Scraper

A Python web scraper for extracting course offerings from the University of Washington's time schedule website. This tool fetches course data including schedules, instructors, enrollment information, and more, then saves it as structured JSON data.

## Features

- 🎯 **Targeted Scraping**: Scrape specific departments or all departments
- 📅 **Multi-Season Support**: Works with Autumn, Winter, Spring, and Summer quarters
- 📊 **Structured Data**: Organizes courses with main sections, labs, and quiz sections
- 💾 **JSON Output**: Clean, structured JSON format for easy data processing
- 🛠️ **Command Line Interface**: Easy-to-use CLI with helpful options
- 📁 **Flexible Output**: Customizable output directories

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/uw-web-scraper.git
   cd uw-web-scraper
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install beautifulsoup4 requests
   ```

## Usage

### Basic Usage

**Scrape a specific department:**
```bash
python3 uw_course_scraper.py --department cse
```

**Scrape all departments:**
```bash
python3 uw_course_scraper.py --all
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--season` | Season to scrape (AUT, WIN, SPR, SUM) | SPR |
| `--year` | Year to scrape | 2025 |
| `--department` | Specific department (e.g., cse, math, phys) | None |
| `--all` | Scrape all departments | False |
| `--output-dir` | Output directory for results | course_offerings |
| `--help` | Show help message | - |

### Examples

**Scrape CSE courses for Spring 2025:**
```bash
python3 uw_course_scraper.py --department cse
```

**Scrape all departments for Winter 2025:**
```bash
python3 uw_course_scraper.py --all --season WIN --year 2025
```

**Scrape Math courses and save to custom directory:**
```bash
python3 uw_course_scraper.py --department math --output-dir my_courses
```

**Scrape Physics courses for Autumn 2024:**
```bash
python3 uw_course_scraper.py --department phys --season AUT --year 2024
```

## Output Format

The scraper generates JSON files with the following structure:

```json
{
  "CSE 121": {
    "CSE 121A": {
      "main_course": {
        "restrictions": [],
        "add_code": "12667",
        "section": "A",
        "is_quiz": false,
        "is_lab": false,
        "credits": "4",
        "credits_vary": false,
        "class_times": [
          {
            "days": "WF",
            "time": "330-420",
            "building": "KNE",
            "room": "120"
          }
        ],
        "c/nc": false,
        "course_fee": "0",
        "other_codes": "",
        "is_estimate": false,
        "max_capacity": "300",
        "curr_enrolled": "194",
        "open_or_closed": "Open",
        "professor_name": "Natsuhara,Miya",
        "curr_course_code": "CSE 121",
        "curr_course_name": "COMP PROGRAMMING I",
        "curr_course_fulfills": ["NSc", "RSN"]
      },
      "quiz_list": [
        {
          "section": "AA",
          "is_quiz": true,
          "class_times": [...],
          "professor_name": "Jagtap,Janvi",
          ...
        }
      ],
      "lab_list": [...]
    }
  }
}
```

### Data Fields

| Field | Description |
|-------|-------------|
| `restrictions` | Course restrictions (prerequisites, etc.) |
| `add_code` | Registration add code |
| `section` | Section identifier |
| `is_quiz` | Whether this is a quiz section |
| `is_lab` | Whether this is a lab section |
| `credits` | Number of credits |
| `credits_vary` | Whether credits vary |
| `class_times` | Array of class meeting times and locations |
| `c/nc` | Credit/No Credit option available |
| `course_fee` | Additional course fees |
| `max_capacity` | Maximum enrollment |
| `curr_enrolled` | Current enrollment |
| `open_or_closed` | Registration status |
| `professor_name` | Instructor name |
| `curr_course_fulfills` | Requirements this course fulfills |

## Example Results

Check the `example_results/` directory for sample output files:

- `sample_cse_courses.json` - Small sample of CSE courses
- `cse_course_offerings_SPR_2025` - Full CSE course data for Spring 2025

## File Structure

```
uw-web-scraper/
├── uw_course_scraper.py      # Main scraper script
├── newScraper.py             # Original scraper (legacy)
├── example_results/          # Sample output files
│   ├── sample_cse_courses.json
│   └── cse_course_offerings_SPR_2025
├── course_offerings_spr_25/  # Generated course data
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

## Dependencies

- **beautifulsoup4**: HTML parsing
- **requests**: HTTP requests
- **json**: JSON data handling (built-in)
- **argparse**: Command line argument parsing (built-in)

## Troubleshooting

### Common Issues

**"No departments found" error:**
- Check your internet connection
- Verify the season/year combination is valid
- UW's website might be temporarily unavailable

**"No courses found" error:**
- The department might not offer courses in that quarter
- Check the department name spelling
- Try a different season/year

**Permission errors:**
- Make sure you have write permissions in the output directory
- Try running with a different output directory

### Getting Help

If you encounter issues:

1. Check that all dependencies are installed
2. Verify your Python version (3.6+)
3. Try running with `--help` to see all options
4. Check the example results to understand expected output format

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Disclaimer

This tool is for educational and research purposes. Please respect UW's website terms of service and don't overload their servers with excessive requests. The data scraped should be used responsibly and in accordance with UW's policies.

## Acknowledgments

- University of Washington for providing the course schedule data
- Beautiful Soup and Requests libraries for making web scraping possible