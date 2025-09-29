import argparse
import requests
import os
import webbrowser
import time
import shutil
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import init, Fore, Back, Style
from datetime import datetime
from urllib.parse import quote_plus, urlparse, parse_qs

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

def _build_session(user_agent_profile="chrome", proxy_url=None, insecure=False, timeout=15):
    """Build a configured requests Session with UA, optional proxy, and SSL options."""
    session = requests.Session()
    user_agents = {
        "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    }
    ua = user_agents.get(user_agent_profile, user_agents["chrome"])
    session.headers.update({
        "User-Agent": ua,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    })
    if proxy_url:
        session.proxies.update({
            "http": proxy_url,
            "https": proxy_url,
        })
    # Attach settings
    session.verify = False if insecure else True
    session.request = _wrap_with_timeout(session.request, timeout)
    return session

def _wrap_with_timeout(request_fn, timeout):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return request_fn(method, url, **kwargs)
    return wrapped

def _google_extract_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    # Google SERP links often in a[href^="/url?q="]
    for a in soup.select('a[href^="/url?q="]'):
        href = a.get('href')
        try:
            # Format: /url?q=https://target&sa=...
            parsed = urlparse(href)
            qs = parse_qs(parsed.query)
            target = qs.get('q', [None])[0]
            if target and not target.startswith('https://www.google.'):
                links.append(target)
        except Exception:
            continue
    # Fallback: result block h3 > a
    if not links:
        for a in soup.select('div.yuRUbf > a[href], h3 ~ a[href]'):
            href = a.get('href')
            if href and href.startswith('http'):
                links.append(href)
    return links

def google_search(query, num_results=10, auto_open=False, timeout=15, retries=3, backoff=1.5, insecure=False, user_agent_profile="chrome", proxy_url=None):
    """Scrape Google SERP and return external result links."""
    try:
        print(f"\n{COLORS['info']}{SYMBOLS['search']} Searching (Google): \"{COLORS['highlight']}{query}{COLORS['info']}\"")
        session = _build_session(user_agent_profile=user_agent_profile, proxy_url=proxy_url, insecure=insecure, timeout=timeout)
        results = []
        with tqdm(total=num_results, desc=f"{COLORS['info']}Collecting results", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour="green") as pbar:
            attempt = 0
            while attempt < retries and len(results) < num_results:
                try:
                    q = quote_plus(query)
                    url = f"https://www.google.com/search?q={q}&num={min(50, num_results)}&hl=en"
                    resp = session.get(url)
                    resp.raise_for_status()
                    links = _google_extract_links(resp.text)
                    for link in links:
                        if link and link.startswith("http"):
                            results.append(link)
                            if auto_open:
                                print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{link}")
                                webbrowser.open(link)
                                time.sleep(1.0)
                            pbar.update(1)
                            if len(results) >= num_results:
                                break
                    break
                except Exception as e:
                    attempt += 1
                    if attempt >= retries:
                        raise e
                    wait_s = backoff ** attempt
                    print(f"{COLORS['warning']}{SYMBOLS['warning']} Google failed (attempt {attempt}/{retries}). Retrying in {wait_s:.1f}s...")
                    time.sleep(wait_s)
        print(f"{COLORS['info']}{SYMBOLS['success']} Found {COLORS['highlight']}{len(results)}{COLORS['info']} results (Google)")
        return results[:num_results]
    except Exception as e:
        print(f"{COLORS['error']}{SYMBOLS['error']} Failed to perform Google search: {e}")
        return []

def bing_search(query, num_results=10, auto_open=False, timeout=15, retries=3, backoff=1.5, insecure=False, user_agent_profile="chrome", proxy_url=None):
    """Scrape Bing SERP and return result links."""
    try:
        print(f"\n{COLORS['info']}{SYMBOLS['search']} Searching (Bing): \"{COLORS['highlight']}{query}{COLORS['info']}\"")
        session = _build_session(user_agent_profile=user_agent_profile, proxy_url=proxy_url, insecure=insecure, timeout=timeout)
        results = []
        with tqdm(total=num_results, desc=f"{COLORS['info']}Collecting results", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour="green") as pbar:
            attempt = 0
            while attempt < retries and len(results) < num_results:
                try:
                    q = quote_plus(query)
                    url = f"https://www.bing.com/search?q={q}&count={min(50, num_results)}&setlang=en"
                    resp = session.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for a in soup.select('li.b_algo h2 a[href], h2 a[href]'):
                        href = a.get('href')
                        if href and href.startswith('http'):
                            results.append(href)
                            if auto_open:
                                print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{href}")
                                webbrowser.open(href)
                                time.sleep(1.0)
                            pbar.update(1)
                            if len(results) >= num_results:
                                break
                    break
                except Exception as e:
                    attempt += 1
                    if attempt >= retries:
                        raise e
                    wait_s = backoff ** attempt
                    print(f"{COLORS['warning']}{SYMBOLS['warning']} Bing failed (attempt {attempt}/{retries}). Retrying in {wait_s:.1f}s...")
                    time.sleep(wait_s)
        print(f"{COLORS['info']}{SYMBOLS['success']} Found {COLORS['highlight']}{len(results)}{COLORS['info']} results (Bing)")
        return results[:num_results]
    except Exception as e:
        print(f"{COLORS['error']}{SYMBOLS['error']} Failed to perform Bing search: {e}")
        return []

def startpage_search(query, num_results=10, auto_open=False, timeout=15, retries=3, backoff=1.5, insecure=False, user_agent_profile="safari", proxy_url=None):
    """Scrape Startpage (Google proxy) to emulate Mozilla/Safari friendly results."""
    try:
        print(f"\n{COLORS['info']}{SYMBOLS['search']} Searching (Startpage): \"{COLORS['highlight']}{query}{COLORS['info']}\"")
        session = _build_session(user_agent_profile=user_agent_profile, proxy_url=proxy_url, insecure=insecure, timeout=timeout)
        results = []
        with tqdm(total=num_results, desc=f"{COLORS['info']}Collecting results", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour="green") as pbar:
            attempt = 0
            while attempt < retries and len(results) < num_results:
                try:
                    q = quote_plus(query)
                    url = f"https://www.startpage.com/sp/search?query={q}&hl=en"
                    resp = session.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # New UI selector
                    for a in soup.select('a[data-testid="result-title-a"], a.result-link'):
                        href = a.get('href')
                        if href and href.startswith('http'):
                            results.append(href)
                            if auto_open:
                                print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{href}")
                                webbrowser.open(href)
                                time.sleep(1.0)
                            pbar.update(1)
                            if len(results) >= num_results:
                                break
                    break
                except Exception as e:
                    attempt += 1
                    if attempt >= retries:
                        raise e
                    wait_s = backoff ** attempt
                    print(f"{COLORS['warning']}{SYMBOLS['warning']} Startpage failed (attempt {attempt}/{retries}). Retrying in {wait_s:.1f}s...")
                    time.sleep(wait_s)
        print(f"{COLORS['info']}{SYMBOLS['success']} Found {COLORS['highlight']}{len(results)}{COLORS['info']} results (Startpage)")
        return results[:num_results]
    except Exception as e:
        print(f"{COLORS['error']}{SYMBOLS['error']} Failed to perform Startpage search: {e}")
        return []

def ddg_search(query, num_results=10, auto_open=False, timeout=15, retries=3, backoff=1.5, insecure=False, user_agent_profile="firefox", proxy_url=None):
    """Perform a DuckDuckGo search by scraping the HTML results page.

    Uses the lightweight HTML endpoint which is more stable for scraping.
    """
    try:
        print(f"\n{COLORS['info']}{SYMBOLS['search']} Searching (DuckDuckGo): \"{COLORS['highlight']}{query}{COLORS['info']}\"")
        results = []
        with tqdm(total=num_results, desc=f"{COLORS['info']}Collecting results", 
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", 
                  colour="green") as pbar:
            attempt = 0
            while attempt < retries and len(results) < num_results:
                try:
                    q = quote_plus(query)
                    url = f"https://html.duckduckgo.com/html/?q={q}&kl=en-us"
                    session = _build_session(user_agent_profile=user_agent_profile, proxy_url=proxy_url, insecure=insecure, timeout=timeout)
                    resp = session.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    links = []
                    # Primary selector for DDG HTML
                    for a in soup.select('a.result__a'):
                        href = a.get('href')
                        if href:
                            links.append(href)
                    # Fallback selectors (in case of class changes)
                    if not links:
                        for a in soup.select('a[href]'):
                            href = a.get('href')
                            if href and '/y.js' not in href and 'duckduckgo.com' not in href:
                                links.append(href)
                    for link in links:
                        if link.startswith('/') or link.startswith('https://duckduckgo.com'):
                            continue
                        results.append(link)
                        if auto_open:
                            print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{link}")
                            webbrowser.open(link)
                            time.sleep(1.0)
                        pbar.update(1)
                        if len(results) >= num_results:
                            break
                    break
                except Exception as e:
                    attempt += 1
                    if attempt >= retries:
                        raise e
                    wait_s = backoff ** attempt
                    print(f"{COLORS['warning']}{SYMBOLS['warning']} DDG search failed (attempt {attempt}/{retries}). Retrying in {wait_s:.1f}s...")
                    time.sleep(wait_s)
        print(f"{COLORS['info']}{SYMBOLS['success']} Found {COLORS['highlight']}{len(results)}{COLORS['info']} search results (DuckDuckGo)")
        return results[:num_results]
    except Exception as e:
        print(f"{COLORS['error']}{SYMBOLS['error']} Failed to perform DuckDuckGo search: {e}")
        return []

def aggregate_search(query, num_results, engines_order, auto_open=False, timeout=15, retries=3, backoff=1.5, insecure=False, user_agent_profile="chrome", proxy_url=None):
    """Aggregate results from multiple engines in order until target count reached."""
    aggregated = []
    seen = set()
    def add_links(links):
        for link in links:
            if not link:
                continue
            # Normalize by netloc + path
            try:
                p = urlparse(link)
                key = f"{p.scheme}://{p.netloc}{p.path}"
            except Exception:
                key = link
            if key in seen:
                continue
            seen.add(key)
            aggregated.append(link)
            if len(aggregated) >= num_results:
                return True
        return False

    for engine in engines_order:
        if len(aggregated) >= num_results:
            break
        if engine == "google":
            links = google_search(query, num_results=num_results, auto_open=False, timeout=timeout, retries=retries, backoff=backoff, insecure=insecure, user_agent_profile=user_agent_profile, proxy_url=proxy_url)
        elif engine == "bing":
            links = bing_search(query, num_results=num_results, auto_open=False, timeout=timeout, retries=retries, backoff=backoff, insecure=insecure, user_agent_profile=user_agent_profile, proxy_url=proxy_url)
        elif engine in ("mozilla", "safari", "startpage"):
            links = startpage_search(query, num_results=num_results, auto_open=False, timeout=timeout, retries=retries, backoff=backoff, insecure=insecure, user_agent_profile=user_agent_profile, proxy_url=proxy_url)
        elif engine == "ddg":
            links = ddg_search(query, num_results=num_results, auto_open=False, timeout=timeout, retries=retries, backoff=backoff, insecure=insecure, user_agent_profile=user_agent_profile, proxy_url=proxy_url)
        else:
            links = []
        if add_links(links):
            break

    # Auto-open if requested
    if auto_open:
        for url in aggregated:
            print(f"\n{COLORS['info']}{SYMBOLS['open']} Opening: {COLORS['url']}{url}")
            webbrowser.open(url)
            time.sleep(1.0)
    return aggregated[:num_results]

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

def generate_filename(query):
    """Generate a filename based on the user's search query."""
    # Clean the query to make it suitable for a filename
    # Remove special characters that aren't suitable for filenames
    safe_query = re.sub(r'[^\w\s-]', '', query).strip().lower()
    # Replace spaces with underscores
    safe_query = re.sub(r'[-\s]+', '_', safe_query)
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Limit filename length (some filesystems have limitations)
    if len(safe_query) > 50:
        safe_query = safe_query[:50]
    
    return f"{safe_query}_{timestamp}.txt"

def save_results(results, query):
    """Save search results to a file with a progress display."""
    filename = generate_filename(query)
    loading_animation(f"Saving {len(results)} results to {filename}", 1)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Search Query: {query}\n")
        f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Results Count: {len(results)}\n")
        f.write(f"{'-'*80}\n\n")
        
        for idx, result in enumerate(results, 1):
            f.write(f"Result #{idx}: {result['title']}\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"Description: {result['description']}\n")
            f.write(f"{'-'*80}\n\n")
    
    print(f"{COLORS['info']}{SYMBOLS['save']} Search results saved to {COLORS['highlight']}{filename}")

def main():
    # Setup command line arguments
    parser = argparse.ArgumentParser(description="OSINT Search Tool")
    parser.add_argument("query", type=str, help="Search keyword or parameter")
    parser.add_argument("--num", type=int, default=10, help="Number of search results (default: 10)")
    parser.add_argument("--auto-open", action="store_true", help="Automatically open all results in the browser as they appear")
    parser.add_argument("--save", action="store_true", help="Save search results to a file")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode to choose which links to open")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout for search requests (seconds)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries on search failure")
    parser.add_argument("--provider", type=str, choices=["auto", "google", "bing", "startpage", "ddg", "multi"], default="auto", help="Search provider: auto, google, bing, startpage, ddg, or multi")
    parser.add_argument("--insecure", action="store_true", help="Disable SSL verification for search requests (not recommended)")
    parser.add_argument("--proxy", type=str, default=None, help="HTTP(S) proxy URL (e.g., http://127.0.0.1:8080). Can be used for CroxyProxy")
    parser.add_argument("--ua", type=str, choices=["auto", "chrome", "firefox", "safari"], default="auto", help="User-Agent profile to use")
    args = parser.parse_args()
    
    # Display the banner
    print_banner()
    
    # Perform the search
    print_section("Dive into the Internet")
    results = []
    ua_profile = {
        "auto": "chrome",
        "chrome": "chrome",
        "firefox": "firefox",
        "safari": "safari",
    }[args.ua]

    if args.provider == "google":
        results = google_search(args.query, args.num, args.auto_open, timeout=args.timeout, retries=args.retries, insecure=args.insecure, user_agent_profile=ua_profile, proxy_url=args.proxy)
    elif args.provider == "bing":
        results = bing_search(args.query, args.num, args.auto_open, timeout=args.timeout, retries=args.retries, insecure=args.insecure, user_agent_profile=ua_profile, proxy_url=args.proxy)
    elif args.provider in ("startpage", "mozilla", "safari"):
        results = startpage_search(args.query, args.num, args.auto_open, timeout=args.timeout, retries=args.retries, insecure=args.insecure, user_agent_profile=ua_profile, proxy_url=args.proxy)
    elif args.provider == "ddg":
        results = ddg_search(args.query, args.num, args.auto_open, timeout=args.timeout, retries=args.retries, insecure=args.insecure, user_agent_profile=ua_profile, proxy_url=args.proxy)
    elif args.provider in ("auto", "multi"):
        # Ordered engines: Google -> Bing -> Startpage (Mozilla/Safari) -> DDG
        order = ["google", "bing", "startpage", "ddg"]
        results = aggregate_search(args.query, args.num, order, auto_open=args.auto_open, timeout=args.timeout, retries=args.retries, backoff=1.5, insecure=args.insecure, user_agent_profile=ua_profile, proxy_url=args.proxy)
    
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
        save_results(scraped_results, args.query)
    
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
    print(f"{COLORS['info']}{SYMBOLS['success']} Search completed. Thank you for using FIND WHAT - OSINT Tool!")
    print(f"{COLORS['highlight']}{'─' * width}\n")

if __name__ == "__main__":
    main()