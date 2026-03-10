import re
import requests
import whois
from urllib.parse import urlparse
import datetime

# Regex pattern for URLs (handles http, www, and raw domains with paths like ss5.in/abc)
URL_PATTERN = re.compile(
    r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)'
)

SHORTENERS = {
    'bit.ly', 't.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 'is.gd',
    'buff.ly', 'adf.ly', 'bit.do', 'shorte.st'
}

def extract_urls(text: str) -> list:
    """Extract URLs from text using regex."""
    urls = URL_PATTERN.findall(text)
    # Basic cleanup (sometimes trailing punctuation gets caught)
    cleaned_urls = []
    for url in urls:
        # Strip trailing punctuation
        url = url.rstrip('.,!?\"\')]}')
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        cleaned_urls.append(url)
    return list(set(cleaned_urls))

def expand_url(url: str, timeout: int = 5) -> str:
    """Expand shortened URLs by following redirects."""
    try:
        domain = urlparse(url).netloc.lower()
        if any(shortener in domain for shortener in SHORTENERS) or len(domain) < 8:
            response = requests.head(url, allow_redirects=True, timeout=timeout)
            return response.url
    except requests.RequestException:
        pass # If we fail to expand, just return the original or move on
    return url

def check_domain_age(url: str) -> tuple[int, list]:
    """
    Check domain age using WHOIS.
    Returns (risk_score, triggers)
    """
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
        
    domain = urlparse(url).netloc
    if domain.startswith('www.'):
        domain = domain[4:]
        
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        # Some registrars return a list of dates
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date is None:
            # Often, a failed WHOIS means the domain is very suspicious or unreachable via whois.
            return 85, [f"Could not verify age or suspicious TLD for {domain}"]
            
        age_days = (datetime.datetime.now() - creation_date).days
        
        if age_days < 30:
            return 100, [f"New domain <30 days ({domain})"]
        elif age_days < 90:
            return 70, [f"Recently created domain ({domain})"]
        elif age_days < 365:
            return 30, [] # Minor risk
        else:
            return 0, []
    except Exception:
        # If WHOIS fails (e.g., rate limit, unsupported TLD), treat it with suspicion
        return 85, [f"Failed to check domain age for {domain}"]

def analyze_urls(text: str) -> dict:
    """
    Stage 2: URL Forensics
    - Extract URLs
    - Expand short links
    - Check domain age
    """
    extracted_urls = extract_urls(text)
    
    if not extracted_urls:
        return {
            "score": 0,
            "expanded_urls": None,
            "triggers": []
        }
        
    final_urls = []
    max_risk = 0
    all_triggers = []
    
    for url in extracted_urls:
        expanded = expand_url(url)
        final_urls.append(expanded)
        
        risk, triggers = check_domain_age(expanded)
        max_risk = max(max_risk, risk)
        all_triggers.extend(triggers)
        
        # Simple brand mismatch example context
        # In a real system, you'd cross-reference with brands mentioned in the text.
        
    return {
        "score": max_risk,
        "expanded_urls": final_urls,
        "triggers": all_triggers
    }
