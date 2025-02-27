# FIND WHAT - OSINT TOOL

## Description
FIND WHAT is an OSINT (Open Source Intelligence) search tool designed for investigation and information gathering. This tool utilizes Google search to find relevant web pages, extracts metadata, and provides interactive options for users to analyze the search results efficiently.

## Features 🚀
✅ Advanced Google Search – Perform Google searches with a specified number of results 📊
✅ Auto-Open Links – Automatically open search results in the browser 🌍
✅ Metadata Extraction – Extract titles and descriptions from web pages 🔍
✅ Save Search Results – Store results in a text file for later analysis 📝
✅ Interactive Mode – Choose which links to open with an easy-to-use interface 🎯
✅ Formatted Output – Display results with colors and icons for better readability 🎨

## Requirements
Before running the script, ensure you have the following dependencies installed:

- Python 3.x
- Required Python libraries:
  ```bash
  pip install argparse requests googlesearch-python beautifulsoup4 tqdm colorama
  ```

## Installation
1. Clone the repository or download the script:
   ```bash
   git clone https://github.com/bagaspra16/find-what.git
   ```

## Usage
Run the script using the following command:
```bash
python find_what.py "search query"
```

### Available Options
- `--num <number>` : Specify the number of search results (default: 10)
- `--auto-open` : Automatically open all search results in the web browser
- `--save` : Save the search results to a file
- `--interactive` : Enable interactive mode to choose which links to open

### Example Commands
1. Perform a simple Google search:
   ```bash
   python find_what.py "open source intelligence tools"
   ```
2. Search for 20 results and open them automatically:
   ```bash
   python find_what.py "latest cybersecurity trends" --num 20 --auto-open
   ```
3. Save search results to a file:
   ```bash
   python find_what.py "best OSINT techniques" --save
   ```
4. Run the tool in interactive mode:
   ```bash
   python find_what.py "deep web search" --interactive
   ```

## Interactive Mode
When running the script with the `--interactive` flag, you will be prompted to choose which search result to open. Simply enter the result number to open the corresponding link in your browser.

## Saving Search Results
If the `--save` flag is used, the search results will be saved in `search_results.txt` in the current working directory.

## Notes
- This tool depends on `googlesearch-python`, which may have API limitations depending on usage.
- Ensure your Python environment has internet access to perform searches and fetch web pages.
- Avoid excessive automated searches to prevent getting temporarily blocked by Google.

## Author
Created by bagaspra16 - Contact: bagaspratamajunianika72@gmail.com

