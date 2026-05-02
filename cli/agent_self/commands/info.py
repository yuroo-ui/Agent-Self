"""Show skill details."""
import json
from pathlib import Path

SKILLS_DIR = Path.home() / ".agent-self" / "skills"


def skill_info(name: str):
    """Show detailed info about an installed skill."""
    skill_dir = SKILLS_DIR / name
    
    if not skill_dir.exists():
        print(f"❌ Skill not found: {name}")
        return
    
    meta_path = skill_dir / "meta.json"
    skill_md = skill_dir / "SKILL.md"
    
    # Metadata
    if meta_path.exists():
        with open(meta_path, "r") as f:
            meta = json.load(f)
    else:
        meta = {}
    
    print(f"📦 {name}\n")
    print(f"   Trust Score: {meta.get('trust_score', '?')}/100")
    print(f"   Source: {meta.get('source', 'unknown')}")
    print(f"   Installed: {meta.get('installed_at', 'unknown')}")
    print(f"   Hash: {meta.get('content_hash', '?')}")
    
    if meta.get("dangers"):
        print(f"\n   🚨 Dangers:")
        for d in meta["dangers"]:
            print(f"      {d}")
    
    if meta.get("warnings"):
        print(f"\n   ⚠️ Warnings:")
        for w in meta["warnings"]:
            print(f"      {w}")
    
    # Skill content preview
    if skill_md.exists():
        with open(skill_md, "r") as f:
            content = f.read()
        lines = content.split("\n")
        print(f"\n📄 SKILL.md ({len(lines)} lines):\n")
        for line in lines[:30]:
            print(f"   {line}")
        if len(lines) > 30:
            print(f"\n   ... ({len(lines) - 30} more lines)")
