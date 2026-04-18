import re


CATEGORY_RULES = [
    (
        "urgency",
        15,
        "urgency/coercion language",
        [
            re.compile(r"\burgent\b"),
            re.compile(r"\bimmediately\b"),
            re.compile(r"\bact now\b"),
            re.compile(r"\blimited time\b"),
            re.compile(r"\bexpires soon\b"),
            re.compile(r"\bwithin\s+\d+\s*(?:mins?|minutes?|hours?)\b"),
            re.compile(r"\bfinal (?:warning|notice)\b"),
        ],
    ),
    (
        "account_threat",
        25,
        "account lock/suspension threat",
        [
            re.compile(r"\baccount\s+(?:has\s+been\s+)?(?:locked|blocked|restricted|suspended)\b"),
            re.compile(r"\bunauthorized activity\b"),
            re.compile(r"\bprevent suspension\b"),
            re.compile(r"\bsecurity alert\b"),
            re.compile(r"\bverify your account\b"),
            re.compile(r"\b(?:account\s+)?reactivation\b"),
            re.compile(r"\bpermanent\s+lock(?:out)?\b"),
            re.compile(r"\b(?:avoid|prevent)\s+(?:a\s+)?(?:permanent\s+)?lock(?:out)?\b"),
        ],
    ),
    (
        "credential_harvest",
        30,
        "credential or banking detail request",
        [
            re.compile(r"\bverify\s+(?:your\s+)?(?:identity|details|information)\b"),
            re.compile(r"\bprovide\s+(?:your\s+)?(?:bank|card|account|otp|cvv|pin|password|details?)\b"),
            re.compile(r"\bbank details?\b"),
            re.compile(r"\bkyc\s*(?:update|verification)?\b"),
            re.compile(r"\blogin\s+to\s+verify\b"),
            re.compile(r"\bconfirm\s+(?:your\s+)?password\b"),
            re.compile(r"\blog\s*in\s+now\b"),
        ],
    ),
    (
        "financial_lure",
        20,
        "financial lure / reward bait",
        [
            re.compile(r"\bflat\s*\d{1,3}%\s*off\b"),
            re.compile(r"\bexclusive\b"),
            re.compile(r"\bdirect\s+credit\b"),
            re.compile(r"\bcredit\s+of\s*(?:rs\.?|inr|₹)\s*\d+[\d,]*\b"),
            re.compile(r"\b(?:won|prize|lottery|claim|cashback|bonus|inheritance)\b"),
            re.compile(r"(?:rs\.?|inr|₹)\s*\d+[\d,]*"),
        ],
    ),
    (
        "short_link",
        20,
        "shortened or obfuscated link",
        [
            re.compile(r"\b(?:bit\.ly|tinyurl\.com|t\.ly|is\.gd|goo\.gl|ow\.ly|buff\.ly)\b"),
        ],
    ),
]

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
    for category, weight, trigger_label, patterns in CATEGORY_RULES:
        if any(pattern.search(text_lower) for pattern in patterns):
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
