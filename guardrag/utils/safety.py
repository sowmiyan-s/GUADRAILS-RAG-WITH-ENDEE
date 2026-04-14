"""
Safety and content filtering system for the RAG bot.
Implements tiered data sensitivity levels and guardrails.
"""

from typing import Optional, Dict, List

JAILBREAK_PATTERNS = [
    "ignore previous", "forget your instructions", "ignore all prior",
    "jailbreak", "dan mode", "pretend you are", "act as if you are",
    "you are now", "disregard your", "override your",
]

SENSITIVITY_PROFILES = {
    "Public": {
        "description": "No data classification restrictions. Basic jailbreak protection only.",
        "input_patterns": [],
        "output_patterns": [],
        "badge": "public",
    },
    "Internal": {
        "description": "Suitable for internal business data. Blocks credential and API key exposure.",
        "input_patterns": [
            "api key", "api_key", "password", "secret key", "access token",
            "private key", "credential"
        ],
        "output_patterns": [
            "api_key", "api key", "password", "access_token", "credential",
            "private_key", "bearer token"
        ],
        "badge": "internal",
    },
    "Confidential": {
        "description": "For confidential data. Adds PII protection.",
        "input_patterns": [
            "api key", "api_key", "password", "secret key", "access token",
            "private key", "credential", "social security", "ssn",
            "date of birth", "home address", "phone number", "email address",
            "credit card", "bank account",
        ],
        "output_patterns": [
            "api_key", "api key", "password", "access_token", "credential",
            "private_key", "bearer token", "ssn", "social security",
            "date of birth", "credit card", "bank account",
        ],
        "badge": "confidential",
    },
    "Restricted": {
        "description": "Maximum protection. For highly sensitive or regulated data (HIPAA, GDPR, financial).",
        "input_patterns": [
            "api key", "api_key", "password", "secret key", "access token",
            "private key", "credential", "social security", "ssn",
            "date of birth", "home address", "phone number", "email address",
            "credit card", "bank account", "medical record", "diagnosis",
            "prescription", "patient", "salary", "tax return",
            "financial statement", "trading", "investment",
        ],
        "output_patterns": [
            "api_key", "api key", "password", "access_token", "credential",
            "private_key", "bearer token", "ssn", "social security",
            "date of birth", "credit card", "bank account", "medical record",
            "diagnosis", "prescription", "patient id", "salary", "tax", "financial",
        ],
        "badge": "restricted",
    },
}


def check_input_safety(
    user_input: str,
    sensitivity: str,
    enabled: bool = True
) -> Optional[str]:
    """
    Check user input against jailbreak and sensitivity-level patterns.
    
    Args:
        user_input: The user's input text
        sensitivity: Sensitivity level (Public, Internal, Confidential, Restricted)
        enabled: Whether to enforce guardrails
        
    Returns:
        Error message if blocked, None otherwise
    """
    if not enabled:
        return None
    
    lower = user_input.lower()
    
    # Check jailbreak patterns (always active)
    for pat in JAILBREAK_PATTERNS:
        if pat in lower:
            return "This request has been blocked. Prompt injection and instruction-override attempts are not permitted."
    
    # Check sensitivity-level patterns
    profile = SENSITIVITY_PROFILES.get(sensitivity, SENSITIVITY_PROFILES["Internal"])
    for pat in profile["input_patterns"]:
        if pat in lower:
            return f"This request has been blocked under the active **{sensitivity}** data sensitivity policy."
    
    return None


def check_output_safety(
    response: str,
    sensitivity: str,
    enabled: bool = True
) -> Optional[str]:
    """
    Check LLM output against sensitivity-level patterns.
    
    Args:
        response: The LLM's response text
        sensitivity: Sensitivity level (Public, Internal, Confidential, Restricted)
        enabled: Whether to enforce guardrails
        
    Returns:
        Redaction message if blocked, None otherwise
    """
    if not enabled:
        return None
    
    lower = response.lower()
    profile = SENSITIVITY_PROFILES.get(sensitivity, SENSITIVITY_PROFILES["Internal"])
    
    for pat in profile["output_patterns"]:
        if pat in lower:
            return f"[REDACTED — Output blocked by {sensitivity} data sensitivity policy.]"
    
    return None


def get_sensitivity_profiles() -> Dict[str, Dict]:
    """Get all available sensitivity profiles with descriptions."""
    return {
        k: {
            "description": v["description"],
            "badge": v["badge"]
        }
        for k, v in SENSITIVITY_PROFILES.items()
    }
