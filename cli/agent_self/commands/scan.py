"""Scan a SKILL.md file for security issues."""
from agent_self.scanner import scan_file


def scan_skill(path: str):
    """Scan a skill file and display results."""
    print(f"🔍 Scanning: {path}\n")
    
    result = scan_file(path)
    
    print(f"📊 Trust Score: {result.trust_score}/100")
    print(f"   {result.summary}\n")
    
    if result.dangers:
        print("🚨 Dangers:")
        for d in result.dangers:
            print(f"   {d}")
        print()
    
    if result.warnings:
        print("⚠️ Warnings:")
        for w in result.warnings:
            print(f"   {w}")
        print()
    
    if result.safe and result.trust_score >= 80:
        print("✅ This skill looks safe to install!")
    elif result.trust_score >= 30:
        print("⚠️ Review the warnings before installing.")
    else:
        print("🚫 This skill has serious security issues. Do not install.")
