"""Skill scanner — security checks for SKILL.md files."""
import re
from dataclasses import dataclass, field
from typing import List

# Dangerous patterns that suggest malicious intent
DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/", "Destructive file deletion command"),
    (r"curl\s+.*\|\s*bash", "Piped shell execution from network"),
    (r"wget\s+.*\|\s*bash", "Piped shell execution from network"),
    (r"chmod\s+777", "Overly permissive file permissions"),
    (r"eval\s*\(", "Dynamic code evaluation"),
    (r"exec\s*\(", "Dynamic code execution"),
    (r"subprocess\.(call|run|Popen)\s*\(", "Subprocess execution"),
    (r"os\.system\s*\(", "OS command execution"),
    (r"__import__\s*\(", "Dynamic module import"),
    (r"open\s*\(\s*['\"].*['\"]\s*,\s*['\"]w", "File write access"),
    (r"/etc/passwd", "System file access"),
    (r"/etc/shadow", "Password file access"),
    (r"private[_-]?key", "Private key access"),
    (r"password|secret|token", "Credential references"),
    (r"\$\(.*\)", "Shell command substitution"),
    (r"`.*`", "Backtick command execution"),
    (r"import\s+socket", "Network socket access"),
    (r"import\s+telnetlib", "Telnet access"),
    (r"base64\.decode", "Base64 decoding (potential obfuscation)"),
]

# Warning patterns — not dangerous alone but worth noting
WARNING_PATTERNS = [
    (r"https?://[^\s)]+", "External URL references"),
    (r"pip\s+install", "Package installation commands"),
    (r"apt[-get]?\s+install", "System package installation"),
    (r"npm\s+install", "Node package installation"),
    (r"sudo", "Privilege escalation"),
]

SUSPICIOUS_TAGS = ["exploit", "payload", "shellcode", "backdoor", "rootkit", "keylogger"]


@dataclass
class ScanResult:
    safe: bool = True
    trust_score: float = 100.0
    dangers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self):
        return {
            "safe": self.safe,
            "trust_score": round(self.trust_score, 1),
            "dangers": self.dangers,
            "warnings": self.warnings,
            "summary": self.summary,
        }


def scan_skill_md(content: str) -> ScanResult:
    """Scan SKILL.md content for security issues."""
    result = ScanResult()

    # Check dangerous patterns (each costs 20 points)
    for pattern, reason in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            result.dangers.append(f"🚨 {reason} (found {len(matches)}x)")
            result.trust_score -= 20 * len(matches)
            result.safe = False

    # Check warning patterns (each costs 5 points)
    for pattern, reason in WARNING_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            result.warnings.append(f"⚠️ {reason} (found {len(matches)}x)")
            result.trust_score -= 5

    # Check for suspicious tags
    content_lower = content.lower()
    for tag in SUSPICIOUS_TAGS:
        if tag in content_lower:
            result.dangers.append(f"🚨 Suspicious keyword: '{tag}'")
            result.trust_score -= 25
            result.safe = False

    # Clamp score
    result.trust_score = max(0.0, min(100.0, result.trust_score))

    # Summary
    if result.trust_score >= 80:
        result.summary = "✅ Looks clean"
    elif result.trust_score >= 60:
        result.summary = "⚠️ Minor warnings, review recommended"
    elif result.trust_score >= 30:
        result.summary = "⚠️ Suspicious — review carefully"
    else:
        result.summary = "🚫 Dangerous — install not recommended"

    return result


def scan_file(path: str) -> ScanResult:
    """Scan a SKILL.md file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return ScanResult(
            safe=False,
            trust_score=0,
            dangers=[f"File not found: {path}"],
            summary="❌ File not found",
        )
    return scan_skill_md(content)
