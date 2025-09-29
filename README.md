## FIND WHAT - OSINT TOOL

### Description
FIND WHAT is an OSINT (Open Source Intelligence) tool for searching, collecting, and presenting information from the web. It now supports multi-engine search (Google → Bing → Startpage → DuckDuckGo), a results aggregator with de-duplication, optional proxy (including CroxyProxy), custom User-Agent profiles, and robust retry/backoff.

### Features 🚀
- **Multi-engine search**: Google, Bing, Startpage (Mozilla/Safari-friendly), DuckDuckGo
- **Aggregator with de-duplication**: Fills up to `--num` results across engines
- **Proxy support**: Use `--proxy` (works with CroxyProxy or any HTTP(S) proxy)
- **User-Agent profiles**: `chrome`, `firefox`, `safari` via `--ua`
- **Retry + backoff**: More resilient to rate limits/network hiccups
- **Auto-open**: Automatically open results in the browser
- **Light webpage extraction**: Title + short description
- **Save to file**: Nicely formatted `.txt`
- **Interactive mode**: Pick which links to open
- **Colored output**: Easier to read in terminal

### Requirements
- Python 3.9+ (Python 3.13 recommended like the example venv)
- Python packages:
  ```bash
  pip install argparse requests beautifulsoup4 tqdm colorama
  ```

### Installation
```bash
git clone https://github.com/bagaspra16/find-what.git
cd find-what
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r <(printf "requests\nbeautifulsoup4\ntqdm\ncolorama\nargparse\n")
```

## Basic Usage
```bash
python find_what.py "your keywords"
```

## Full CLI Options
- **--num <int>**: Number of results. Default: 10
- **--auto-open**: Automatically open each found URL
- **--save**: Save results to `.txt` named `<query>_YYYYMMDD_HHMMSS.txt`
- **--interactive**: Interactive mode to pick links to open
- **--timeout <int>**: HTTP timeout (seconds). Default: 15
- **--retries <int>**: Number of retries on failure. Default: 3
- **--provider <auto|google|bing|startpage|ddg|multi>**: Search provider. Default: `auto`
  - `auto`/`multi`: aggregate in order Google → Bing → Startpage → DuckDuckGo
  - `google`: force Google
  - `bing`: force Bing
  - `startpage`: force Startpage (good for Mozilla/Safari-like UA)
  - `ddg`: force DuckDuckGo HTML
- **--proxy <url>**: HTTP(S) proxy (e.g., `http://127.0.0.1:8080`). Useful for CroxyProxy
- **--ua <auto|chrome|firefox|safari>**: User-Agent profile to use. Default: `auto` (= `chrome`)
- **--insecure**: Disable SSL verification for search requests (not recommended; only for SSL inspection environments)

## Advanced Examples

### 1) Multi-engine search with save
```bash
python find_what.py "osint framework" --num 20 --save --provider multi
```

### 2) Auto-open with aggregator
```bash
python find_what.py "latest cybersecurity trends" --num 5 --auto-open --provider multi
```

### 3) Interactive mode
```bash
python find_what.py "deep web search techniques" --interactive
```

### 4) Tune network resilience: timeout + retries
```bash
python find_what.py "threat intel feeds" --timeout 30 --retries 4
```

### 5) Force a specific engine
```bash
python find_what.py "osint email enumeration" --provider ddg --num 10
python find_what.py "breach news" --provider bing --num 10
python find_what.py "advanced recon" --provider startpage --num 10 --ua safari
```

### 6) Use a proxy/CroxyProxy
```bash
python find_what.py "bug bounty recon" --provider multi --proxy http://127.0.0.1:8080
```

### 7) Change User-Agent profile
```bash
python find_what.py "cve-2024 poc" --ua firefox
```

### 8) Strict networks / SSL inspection (avoid when possible)
```bash
python find_what.py "supply chain compromise" --provider ddg --insecure --timeout 20 --retries 2
```

## Fallback and Resilience Behavior
- **Auto/multi provider**: iterates Google → Bing → Startpage → DuckDuckGo until `--num` results collected, with de-duplication
- **Retry + backoff**: retries failures with exponential delays
- **Timeout**: prevents hangs on slow networks or unresponsive servers

## Output and Saving
- Results include number, title, URL, and short description
- `--save` writes to `<query_sanitized>_YYYYMMDD_HHMMSS.txt` in the current directory

## Best Practices
- **Avoid excessive frequency** to reduce rate-limits (e.g., Google 429)
- Try **--provider ddg** when Google denies requests
- Increase **--timeout** on slow networks and **--retries** on unstable connections
- Avoid **--insecure** unless your environment enforces SSL inspection

## Troubleshooting
- **429 Too Many Requests (Google)**:
  - Re-run with `--provider ddg` or `--provider multi`
  - Reduce `--num`, increase `--timeout`, raise `--retries`
- **SSL: CERTIFICATE_VERIFY_FAILED**:
  - Try `--provider ddg` (endpoint: `https://html.duckduckgo.com/html/`)
  - If your network performs SSL inspection, use `--proxy` and, if necessary, `--insecure` (security risk)
- **Empty results**:
  - Adjust keywords (be more specific) or increase `--num`
  - Use `--provider multi` to leverage more engines
- **Too many tabs**:
  - Remove `--auto-open` or reduce `--num`

## Notes
- SERP HTML may change over time; selectors include fallbacks, but scraping can break. Use `--provider multi` or switch engines if needed
- Respect websites' terms of service. Be mindful of load

## Author
Created by bagaspra16 — contact: bagaspratamajunianika72@gmail.com
