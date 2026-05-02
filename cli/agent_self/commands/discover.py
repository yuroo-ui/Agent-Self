"""Discover skills from the network — search GitHub for SKILL.md files."""
import json
import urllib.request
import urllib.parse
from typing import Optional


def discover_skills(query: Optional[str] = None, tag: Optional[str] = None, limit: int = 10):
    """Discover skills by searching GitHub for SKILL.md files."""
    
    search_query = "filename:SKILL.md"
    if query:
        search_query += f" {query}"
    if tag:
        search_query += f" tag:{tag}"
    
    print(f"🔍 Searching skills: \"{query or 'all'}\"\n")
    
    # Search GitHub code search API (no auth needed for public repos)
    encoded = urllib.parse.quote(search_query)
    url = f"https://api.github.com/search/code?q={encoded}&per_page={limit}"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Agent-Self/0.5",
            "Accept": "application/vnd.github.v3+json",
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"❌ Search failed: {e}")
        print("   Tip: You can install directly from URL instead:")
        print("   agent-self skill install <github-url>")
        return
    
    items = data.get("items", [])
    
    if not items:
        print("📭 No skills found matching your query.")
        print("   Try: agent-self skill install <url> to install manually")
        return
    
    print(f"📦 Found {len(items)} skills:\n")
    
    for i, item in enumerate(items[:limit], 1):
        repo_name = item["repository"]["full_name"]
        file_path = item["path"]
        html_url = item["html_url"]
        
        # Extract skill name from path
        parts = file_path.split("/")
        skill_name = parts[0] if len(parts) > 1 else file_path.replace(".md", "")
        
        # Build install command
        install_cmd = f"agent-self skill install github:{repo_name}/{file_path}"
        
        print(f"  {i}. 📦 {skill_name}")
        print(f"     Repo: {repo_name}")
        print(f"     Path: {file_path}")
        print(f"     Install: {install_cmd}")
        print()
    
    print("💡 To install: copy one of the commands above")
