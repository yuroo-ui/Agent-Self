"""List installed skills."""
import json
from pathlib import Path

SKILLS_DIR = Path.home() / ".agent-self" / "skills"


def list_skills():
    """List all installed skills."""
    index_path = SKILLS_DIR / "index.json"
    
    if not index_path.exists():
        print("📭 No skills installed yet.")
        print("   Install one: agent-self skill install <url>")
        return
    
    with open(index_path, "r") as f:
        index = json.load(f)
    
    skills = index.get("skills", {})
    
    if not skills:
        print("📭 No skills installed yet.")
        return
    
    print(f"📦 Installed Skills ({len(skills)}):\n")
    
    for name, info in skills.items():
        skill_dir = Path(info["path"])
        meta_path = skill_dir / "meta.json"
        
        if meta_path.exists():
            with open(meta_path, "r") as f:
                meta = json.load(f)
            trust = meta.get("trust_score", "?")
            source = meta.get("source", "unknown")
        else:
            trust = "?"
            source = "unknown"
        
        # Read description from SKILL.md first line
        skill_md = skill_dir / "SKILL.md"
        desc = ""
        if skill_md.exists():
            with open(skill_md, "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        desc = line.strip()[:80]
                        break
        
        print(f"  🟢 {name}")
        print(f"     Trust: {trust}/100 | {desc}")
        print(f"     Source: {source[:60]}")
        print()
