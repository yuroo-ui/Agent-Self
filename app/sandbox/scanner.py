"""Skill Sandbox Scanner - Security analysis for submitted skills.

Performs:
1. Static analysis (code patterns, malware signatures)
2. Permission audit (what the skill accesses)
3. Network analysis (suspicious connections)
4. Dependency check (known safe/unsafe packages)
"""

import hashlib
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ScanResult(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Finding:
    """A single scan finding."""
    rule: str
    message: str
    severity: Severity
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None


@dataclass
class ScanReport:
    """Complete scan report for a skill."""
    result: ScanResult
    trust_score: float  # 0.0 - 100.0
    findings: list[Finding] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    content_hash: str = ""
    scan_duration_ms: int = 0
    
    def to_dict(self):
        return {
            "result": self.result.value,
            "trust_score": self.trust_score,
            "findings": [
                {
                    "rule": f.rule,
                    "message": f.message,
                    "severity": f.severity.value,
                    "line_number": f.line_number,
                }
                for f in self.findings
            ],
            "permissions": self.permissions,
            "dependencies": self.dependencies,
            "content_hash": self.content_hash,
            "scan_duration_ms": self.scan_duration_ms,
        }


# === Dangerous patterns to detect ===

DANGEROUS_IMPORTS = {
    "os.system": ("Executes shell commands", Severity.CRITICAL),
    "subprocess": ("Spawns subprocesses", Severity.CRITICAL),
    "eval": ("Evaluates arbitrary code", Severity.CRITICAL),
    "exec": ("Executes arbitrary code", Severity.CRITICAL),
    "__import__": ("Dynamic imports", Severity.WARNING),
    "ctypes": ("Low-level C calls", Severity.WARNING),
    "signal": ("Process signals", Severity.WARNING),
    "pty": ("Pseudo-terminal access", Severity.WARNING),
}

SUSPICIOUS_PATTERNS = {
    r"socket\.": ("Raw socket access", Severity.WARNING),
    r"requests\.(get|post|put|delete)\(": ("HTTP requests", Severity.INFO),
    r"open\(.+(?:w|wb)": ("File write access", Severity.INFO),
    r"/etc/passwd": ("System file access", Severity.CRITICAL),
    r"/etc/shadow": ("Password file access", Severity.CRITICAL),
    r"\.ssh/": ("SSH key access", Severity.CRITICAL),
    r"\.env": ("Environment variable access", Severity.WARNING),
    r"password|passwd|secret|token|api_key": ("Credential patterns", Severity.WARNING),
}

DATA_EXFIL_PATTERNS = {
    r"requests\.(get|post)\s*\(\s*['\"]https?://(?!localhost|127\.0\.0\.1)": ("External HTTP call", Severity.WARNING),
    r"urllib\.request\.urlopen": ("URL opening", Severity.WARNING),
    r"smtplib": ("Email sending", Severity.WARNING),
    r"ftplib": ("FTP access", Severity.WARNING),
    r"telnetlib": ("Telnet access", Severity.CRITICAL),
}


class SkillScanner:
    """Main scanner class for skill security analysis."""
    
    def scan(self, code: str, manifest: Optional[dict] = None) -> ScanReport:
        """Run full security scan on skill code."""
        start_time = time.time()
        findings: list[Finding] = []
        
        # Calculate content hash
        content_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # 1. Static analysis - dangerous imports
        findings.extend(self._scan_dangerous_imports(code))
        
        # 2. Pattern matching - suspicious code
        findings.extend(self._scan_patterns(code, SUSPICIOUS_PATTERNS, "suspicious"))
        
        # 3. Data exfiltration detection
        findings.extend(self._scan_patterns(code, DATA_EXFIL_PATTERNS, "exfiltration"))
        
        # 4. Permission audit
        permissions = self._audit_permissions(code)
        
        # 5. Dependency check
        dependencies = self._extract_dependencies(code, manifest)
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(findings)
        
        # Determine overall result
        result = self._determine_result(findings, trust_score)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return ScanReport(
            result=result,
            trust_score=trust_score,
            findings=findings,
            permissions=permissions,
            dependencies=dependencies,
            content_hash=content_hash,
            scan_duration_ms=duration_ms,
        )
    
    def _scan_dangerous_imports(self, code: str) -> list[Finding]:
        """Scan for dangerous import patterns."""
        findings = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            for pattern, (msg, severity) in DANGEROUS_IMPORTS.items():
                if pattern in line:
                    findings.append(Finding(
                        rule=f"dangerous_import:{pattern}",
                        message=msg,
                        severity=severity,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                    ))
        return findings
    
    def _scan_patterns(self, code: str, patterns: dict, category: str) -> list[Finding]:
        """Scan code against regex patterns."""
        findings = []
        lines = code.split("\n")
        
        for i, line in enumerate(lines, 1):
            for pattern, (msg, severity) in patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        rule=f"{category}:{pattern}",
                        message=msg,
                        severity=severity,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                    ))
        return findings
    
    def _audit_permissions(self, code: str) -> list[str]:
        """Identify what permissions/resources the skill accesses."""
        permissions = []
        
        if "os." in code or "subprocess" in code:
            permissions.append("system:shell")
        if "open(" in code or "File" in code:
            permissions.append("filesystem:read_write")
        if "socket" in code or "requests" in code:
            permissions.append("network:internet")
        if "getpass" in code or "password" in code.lower():
            permissions.append("sensitive:credentials")
        if "cv2" in code or "PIL" in code or "pillow" in code.lower():
            permissions.append("media:images")
        if "speech" in code.lower() or "audio" in code.lower():
            permissions.append("media:audio")
        
        return permissions
    
    def _extract_dependencies(self, code: str, manifest: Optional[dict]) -> list[str]:
        """Extract dependencies from code and manifest."""
        deps = []
        
        if manifest and "dependencies" in manifest:
            deps.extend(manifest["dependencies"])
        
        # Detect common imports
        import_patterns = re.findall(r'(?:from|import)\s+(\w+)', code)
        deps.extend(set(import_patterns))
        
        return list(set(deps))
    
    def _calculate_trust_score(self, findings: list[Finding]) -> float:
        """Calculate trust score based on findings."""
        score = 100.0
        
        for finding in findings:
            if finding.severity == Severity.CRITICAL:
                score -= 25.0
            elif finding.severity == Severity.WARNING:
                score -= 5.0
            elif finding.severity == Severity.INFO:
                score -= 1.0
        
        return max(0.0, min(100.0, score))
    
    def _determine_result(self, findings: list[Finding], trust_score: float) -> ScanResult:
        """Determine overall scan result."""
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        warning_count = sum(1 for f in findings if f.severity == Severity.WARNING)
        
        if critical_count > 0:
            return ScanResult.MALICIOUS
        elif warning_count > 3 or trust_score < 50:
            return ScanResult.SUSPICIOUS
        else:
            return ScanResult.CLEAN


# Singleton scanner instance
scanner = SkillScanner()
