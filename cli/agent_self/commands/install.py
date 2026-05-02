"""Install command — fetch SKILL.md from URL or file, scan, and install."""
import os
import json
import shutil
import hashlib
import urllib.request
from datetime import datetime
from pathlib import Path

from agent_self.scanner import scan_skill_md, scan_file

SKILLS_DIR = Path.home() / ".agent-self" / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


def resolve_source(source: str) -> tuple[str, str]:
    """
    Resolve source to (raw_content, skill_name).
    
    Supports:
    - Full URL: https://raw.githubusercontent.com/user/repo/main/SKILL.md
    - GitHub shorthand: github:user/repo/SKILL.md or user/repo/SKILL.md
    - Local file: ./path/to/SKILL.md or /absolute/path/SKILL.md
    """
    # Local file
    if source.startswith("./") or source.startswith("/") or os.path.isfile(source):
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
        name = Path(source).parent.name
        return content, name

    # GitHub shorthand
    if source.startswith("github:"):
        source = source[7:]
    
    if "/" in source and not source.startswith("http"):
        # Assume github:user/repo/path
        parts = source.split("/")
        if len(parts) >= 3:
            user, repo = parts[0], parts[1]
            path = "/".join(parts[2:])
            url = f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}"
            # Try main branch first, then master
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Agent-Self/0.5"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8")
                    name = repo
                    return content, name
            except Exception:
                # Try master branch
                url = url.replace("/main/", "/master/")
                req = urllib.request.Request(url, headers={"User-Agent": "Agent-Self/0.5"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8")
                    name = repo
                    return content, name

    # Full URL
    if source.startswith("http"):
        req = urllib.request.Request(source, headers={"User-Agent": "Agent-Self/0.5"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            # Extract name from URL path
            path_parts = source.rstrip("/").split("/")
            name = path_parts[-2] if path_parts[-1] == "SKILL.md" else path_parts[-1].replace(".md", "")
            return content, name

    raise ValueError(f"Cannot resolve source: {source}")


def install_skill(source: str, force: bool = False):
    """Install a skill from URL, GitHub shorthand, or local file."""
    print(f"🔍 Fetching skill: {source}")

    try:
        content, name = resolve_source(source)
    except Exception as e:
        print(f"❌ Failed to fetch: {e}")
        return

    print(f"📦 Skill: {name}")
    
    # Scan for security
    print("🛡️ Scanning for security issues...")
    from agent_self.scanner import scan_skill_md
    result = scan_skill_md(content)
    
    print(f"   Trust Score: {result.trust_score}/100")
    print(f"   {result.summary}")
    
    for danger in result.dangers:
        print(f"   {danger}")
    for warning in result.warnings:
        print(f"   {warning}")
    
    # Block dangerous skills
    if result.trust_score < 30 and not force:
        print(f"\n🚫 Skill blocked (trust score {result.trust_score} < 30)")
        print("   Use --force to install anyway (not recommended)")
        return
    
    if result.trust_score < 60 and not force:
        print(f"\n⚠️ Low trust score ({result.trust_score}). Use --force to install.")
        return

    # Install to skills directory
    skill_dir = SKILLS_DIR / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    skill_path = skill_dir / "SKILL.md"
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Write metadata
    meta = {
        "name": name,
        "source": source,
        "installed_at": datetime.utcnow().isoformat(),
        "trust_score": result.trust_score,
        "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
        "warnings": result.warnings,
        "dangers": result.dangers,
    }
    meta_path = skill_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    
    print(f"\n✅ Installed: {name} → {skill_dir}")
    print(f"   Skill file: {skill_path}")
    
    # Add to active skills list
    _update_skills_index(name, skill_dir)


def _update_skills_index(name: str, skill_dir: Path):
    """Add skill to the skills index."""
    index_path = SKILLS_DIR / "index.json"
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {"skills": {}}
    
    index["skills"][name] = {
        "path": str(skill_dir),
        "installed": datetime.utcnow().isoformat(),
    }
    
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
