"""Remove an installed skill."""
import json
from pathlib import Path

SKILLS_DIR = Path.home() / ".agent-self" / "skills"


def remove_skill(name: str):
    """Remove an installed skill."""
    skill_dir = SKILLS_DIR / name
    
    if not skill_dir.exists():
        print(f"❌ Skill not found: {name}")
        return
    
    # Remove directory
    import shutil
    shutil.rmtree(skill_dir)
    
    # Update index
    index_path = SKILLS_DIR / "index.json"
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
        index.get("skills", {}).pop(name, None)
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
    
    print(f"🗑️ Removed: {name}")
