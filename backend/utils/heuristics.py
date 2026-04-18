import re

def parse_heuristics(text: str) -> dict:
    """
    Stage 1: Heuristic Analysis (fast regex + keyword rules)
    Returns a dict with:
      - score: int (0-100)
      - triggers: list of matching string patterns/reasons
    """
    score = 0
    triggers = []

    text_lower = text.lower()

    category_matches = {
        "urgency": False,
        "account_threat": False,
        "credential_harvest": False,
        "financial_lure": False,
        "short_link": False,
    }

    # Match at most once per category to avoid over-penalizing duplicates.
    categories = [
        (
            "urgency",
            15,
            "urgency/coercion language",
            [
                r"\burgent\b",
                r"\bimmediately\b",
                r"\bact now\b",
                r"\blimited time\b",
                r"\bexpires soon\b",
                r"\bwithin\s+\d+\s*(?:mins?|minutes?|hours?)\b",
                r"\bfinal (?:warning|notice)\b",
            ],
        ),
        (
            "account_threat",
            25,
            "account lock/suspension threat",
            [
                r"\baccount\s+(?:has\s+been\s+)?(?:locked|blocked|restricted|suspended)\b",
                r"\bunauthorized activity\b",
                r"\bprevent suspension\b",
                r"\bsecurity alert\b",
                r"\bverify your account\b",
            ],
        ),
        (
            "credential_harvest",
            30,
            "credential or banking detail request",
            [
                r"\bverify\s+(?:your\s+)?(?:identity|details|information)\b",
                r"\bprovide\s+(?:your\s+)?(?:bank|card|account|otp|cvv|pin|password|details?)\b",
                r"\bbank details?\b",
                r"\bkyc\s*(?:update|verification)?\b",
                r"\blogin\s+to\s+verify\b",
            ],
        ),
        (
            "financial_lure",
            20,
            "financial lure / reward bait",
            [
                r"\bflat\s*\d{1,3}%\s*off\b",
                r"\bexclusive\b",
                r"\bdirect\s+credit\b",
                r"\bcredit\s+of\s*(?:rs\.?|inr|₹)\s*\d+[\d,]*\b",
                r"\b(?:won|prize|lottery|claim|cashback|bonus|inheritance)\b",
                r"(?:rs\.?|inr|₹)\s*\d+[\d,]*",
            ],
        ),
        (
            "short_link",
            20,
            "shortened or obfuscated link",
            [
                r"\b(?:bit\.ly|tinyurl\.com|t\.ly|is\.gd|goo\.gl|ow\.ly|buff\.ly)\b",
            ],
        ),
    ]

    for category, weight, trigger_label, patterns in categories:
        if any(re.search(pattern, text_lower) for pattern in patterns):
            category_matches[category] = True
            score += weight
            triggers.append(trigger_label)

    # Composite scam boosters
    if category_matches["account_threat"] and category_matches["credential_harvest"]:
        score += 20
        triggers.append("account takeover pattern")

    if category_matches["financial_lure"] and category_matches["credential_harvest"]:
        score += 20
        triggers.append("incentive + banking details pattern")

    if category_matches["short_link"] and category_matches["credential_harvest"]:
        score += 10
        triggers.append("short-link credential phishing pattern")

    # Style-based signals
    if re.search(r'!!!!!+', text):
        score += 10
        triggers.append("excessive punctuation (!!!)")

    words = re.findall(r'\b[A-Z]{4,}\b', text)
    if len(words) >= 3:
        score += 10
        triggers.append("excessive ALL CAPS")

    score = min(score, 100)
    
    return {
        "score": score,
        "triggers": triggers
    }
