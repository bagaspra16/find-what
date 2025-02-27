import argparse
import requests
import os
import webbrowser
import time
import shutil
from googlesearch import search
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Color and symbol constants
COLORS = {
    "title": Fore.CYAN + Style.BRIGHT,
    "url": Fore.BLUE + Style.BRIGHT,
    "desc": Fore.WHITE,
    "info": Fore.GREEN,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "highlight": Fore.MAGENTA + Style.BRIGHT,
    "reset": Style.RESET_ALL
}

SYMBOLS = {
    "search": "🔍",
    "find": "🔎",
    "web": "🌐",
    "open": "🚀",
    "save": "💾",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "success": "✅",
    "clock": "⏱️",
    "link": "🔗",
    "page": "📄",
    "bullet": "•",
    "arrow": "→",
    "star": "★"
}

def print_banner():
    """Display a dynamic application banner based on terminal width."""
    width = shutil.get_terminal_size().columns  # Get current terminal width
    
    banner_text = "FIND WHAT - OSINT TOOL"
    desc_text = "An OSINT search tool for investigation and information gathering"
    
    print(f"\n{COLORS['highlight']}{'─' * width}")
    print(f"{COLORS['highlight']}{SYMBOLS['star']} {COLORS['title']}{banner_text} {COLORS['highlight']}{SYMBOLS['web']}")
    print(f"{COLORS['info']}{desc_text}")
    print(f"{COLORS['highlight']}{'─' * width}")

def print_section(title):
    """Display a section title with a dynamic border."""
    width = shutil.get_terminal_size().columns  # Get current terminal width
    print(f"\n{COLORS['highlight']}{'─' * width}")
    print(f"{COLORS['info']}{SYMBOLS['arrow']} {COLORS['title']}{title}")
    print(f"{COLORS['highlight']}{'─' * width}")

def loading_animation(text, duration=1.5):
    """Display a simple loading animation."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for _ in range(int(duration * 10)):
        for char in chars:
            print(f"\r{COLORS['info']}{char} {text}...", end='')
            time.sleep(0.1)
    print()

def google_search(query, num_results=10, auto_open=False):
    """Perform a Google search and retrieve results, with an option to open results automatically."""
    try:
        print(f"\n{COLORS['info']}{SYMBOLS['search']} Searching: \"{COLORS['highlight']}{query}{COLORS['info']}\"")
        
        results = []
        with tqdm(total=num_results, desc=f"{COLORS['info']}Collecting results", 
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", 
                  colour="green") as pbar:
            for url in search(query, num_results=num_results, lang="en"):
                results.append(url)
                # If auto_open is enabled, open the website as soon as it's found
                if auto_open:
                    print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{url}")
                    webbrowser.open(url)
                    # Short delay to prevent overwhelming the browser
                    time.sleep(1.5)
                pbar.update(1)
        
        print(f"{COLORS['info']}{SYMBOLS['success']} Found {COLORS['highlight']}{len(results)}{COLORS['info']} search results")
        return results
    except Exception as e:
        print(f"{COLORS['error']}{SYMBOLS['error']} Failed to perform search: {e}")
        return []

def scrape_page(url, idx):
    """Scrape a web page to retrieve its title and description."""
    try:
        print(f"\r{COLORS['info']}{SYMBOLS['page']} Collecting information from result {idx}...", end="")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "(No title)"
        desc = "".join([p.text for p in soup.find_all('p')[:2]])[:300]
        desc = desc.replace("\n", " ").strip()
        if desc:
            desc += "..."
        else:
            desc = "(No description)"
        
        return {"url": url, "title": title, "description": desc}
    except Exception as e:
        return {"url": url, "title": "(Failed to retrieve title)", "description": f"Error: {e}"}

def print_result(idx, page_info):
    """Display search results in a neat and dynamic format."""
    width = shutil.get_terminal_size().columns  # Get current terminal width
    
    # Format the title with the result number
    title = page_info['title']
    url = page_info['url']
    desc = page_info['description']
    
    # Result title
    print(f"\n{COLORS['title']}{SYMBOLS['bullet']} Result #{idx}: {title}")
    
    # URL with a different color
    print(f"  {COLORS['url']}{SYMBOLS['link']} {url}")
    
    # Description with text wrapping
    desc_words = desc.split()
    desc_lines = []
    current_line = "  "  # Indent for description
    
    for word in desc_words:
        if len(current_line + " " + word) <= width:
            current_line += " " + word if current_line != "  " else word
        else:
            desc_lines.append(current_line)
            current_line = "  " + word  # New indent for the next line
    
    if current_line != "  ":
        desc_lines.append(current_line)
    
    # Display the description
    for line in desc_lines:
        print(f"{COLORS['desc']}{line}")
    
    # Display a dynamic border at the end of the result
    print(f"{COLORS['highlight']}{'─' * width}")

def save_results(results, filename="search_results.txt"):
    """Save search results to a file with a progress display."""
    loading_animation(f"Saving {len(results)} results to {filename}", 1)
    
    with open(filename, "w", encoding="utf-8") as f:
        for result in results:
            f.write(f"{result['title']} - {result['url']}\n{result['description']}\n{'-'*80}\n")
    
    print(f"{COLORS['info']}{SYMBOLS['save']} Search results saved to {COLORS['highlight']}{filename}")

def main():
    # Setup command line arguments
    parser = argparse.ArgumentParser(description="OSINT Search Tool")
    parser.add_argument("query", type=str, help="Search keyword or parameter")
    parser.add_argument("--num", type=int, default=10, help="Number of search results (default: 10)")
    parser.add_argument("--auto-open", action="store_true", help="Automatically open all results in the browser as they appear")
    parser.add_argument("--save", action="store_true", help="Save search results to a file")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode to choose which links to open")
    args = parser.parse_args()
    
    # Display the banner
    print_banner()
    
    # Perform the search
    print_section("Dive into the Internet")
    results = google_search(args.query, args.num, args.auto_open)
    
    if not results:
        print(f"{COLORS['error']}{SYMBOLS['error']} No results found.")
        return
    
    # Display search results
    print_section("SEARCH RESULTS")
    scraped_results = []
    
    # Loading animation while scraping
    loading_animation("Preparing search results", 1)
    
    for idx, url in enumerate(results, 1):
        page_info = scrape_page(url, idx)
        scraped_results.append(page_info)
        print_result(idx, page_info)
    
    # Save results if requested
    if args.save:
        print_section("SAVING RESULTS")
        save_results(scraped_results)
    
    # Interactive mode
    if args.interactive:
        print_section("INTERACTIVE MODE")
        print(f"{COLORS['info']}Choose a result number to open in the browser or type 'exit' to quit")
        
        while True:
            choice = input(f"\n{COLORS['highlight']}{SYMBOLS['arrow']} Your choice: ")
            if choice.lower() == "exit":
                break
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                idx = int(choice)
                url = results[idx - 1]
                print(f"{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{url}")
                webbrowser.open(url)
            else:
                print(f"{COLORS['warning']}{SYMBOLS['warning']} Invalid choice, please try again.")
    
    width = shutil.get_terminal_size().columns  # Get current terminal width
    print(f"\n{COLORS['highlight']}{'─' * width}")
    print(f"{COLORS['info']}{SYMBOLS['success']} Search completed. Thank you for using the OSINT Search Tool!")
    print(f"{COLORS['highlight']}{'─' * width}\n")

if __name__ == "__main__":
    main()