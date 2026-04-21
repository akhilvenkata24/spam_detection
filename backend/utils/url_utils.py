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
            # WHOIS is sometimes incomplete for legitimate domains, so treat this as a mild signal.
            return 25, [f"Could not verify age for {domain}"]
            
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
        # WHOIS can fail for legitimate domains too, so do not escalate this to a severe risk.
        return 20, [f"Could not verify age for {domain}"]

def check_domain_heuristics(url: str, domain: str) -> tuple[int, list]:
    """
    Check URLs for common phishing/scam heuristics independent of WHOIS.
    Returns (risk_score, triggers)
    """
    score = 0
    triggers = []
    
    # 1. IP Address instead of a domain name (highly suspicious for public links)
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
        score += 80
        triggers.append(f"IP address used instead of domain name: {domain}")
        
    # 2. Suspicious cheap/free TLDs heavily abused by scammers
    suspicious_tlds = ['.xyz', '.top', '.click', '.loan', '.buzz', '.info', '.club', '.stream', '.gq', '.ml', '.cf', '.tk']
    if any(domain.endswith(tld) for tld in suspicious_tlds):
        score += 40
        triggers.append(f"Suspicious TLD used: {domain}")
        
    # 3. Phishing keywords in domain name
    phishing_keywords = ['login', 'verify', 'update', 'secure', 'auth', 'account', 'banking', 'support', 'service', 'validation']
    for kw in phishing_keywords:
        if kw in domain.lower():
            score += 30
            triggers.append(f"Suspicious keyword '{kw}' found in domain: {domain}")
            break
            
    # 4. Excessive hyphens (e.g. secure-login-amazon-update.com)
    if domain.count('-') >= 2:
        score += 20
        triggers.append(f"Multiple hyphens in domain, common in phishing: {domain}")
        
    # 5. Shorteners (if it couldn't be expanded)
    if any(shortener in domain.lower() for shortener in SHORTENERS):
        score += 30
        triggers.append(f"URL shortener used: {domain}")
        
    return min(100, score), triggers

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
        
        # Get domain for heuristic check
        domain = urlparse(expanded if expanded.startswith(('http://', 'https://')) else 'http://' + expanded).netloc
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # 1. Check WHOIS Age
        whois_risk, whois_triggers = check_domain_age(expanded)
        
        # 2. Check Static Heuristics (IPs, TLDs, Hyphens, Keywords)
        heur_risk, heur_triggers = check_domain_heuristics(expanded, domain)
        
        # Combine risks
        combined_risk = max(whois_risk, heur_risk)
        if whois_risk > 0 and heur_risk > 0: # If both flagged, push score higher
            combined_risk = min(100, whois_risk + (heur_risk // 2))
            
        max_risk = max(max_risk, combined_risk)
        all_triggers.extend(whois_triggers)
        all_triggers.extend(heur_triggers)
        
    return {
        "score": max_risk,
        "expanded_urls": final_urls,
        "triggers": all_triggers
    }
