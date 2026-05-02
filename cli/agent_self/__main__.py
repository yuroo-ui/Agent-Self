"""Agent-Self CLI — Agent Skill Manager."""
import sys
import argparse

from agent_self.commands.install import install_skill
from agent_self.commands.list_cmd import list_skills
from agent_self.commands.scan import scan_skill
from agent_self.commands.remove import remove_skill
from agent_self.commands.info import skill_info
from agent_self.commands.discover import discover_skills


def main():
    parser = argparse.ArgumentParser(
        prog="agent-self",
        description="🔧 Agent-Self — Agent Skill Manager",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- skill subcommand ---
    skill_parser = subparsers.add_parser("skill", help="Manage skills")
    skill_sub = skill_parser.add_subparsers(dest="skill_action")

    # skill install
    install_p = skill_sub.add_parser("install", help="Install a skill from URL or file")
    install_p.add_argument("source", help="URL, GitHub shorthand (user/repo/SKILL.md), or local path")
    install_p.add_argument("--force", action="store_true", help="Force install even if trust score is low")

    # skill list
    skill_sub.add_parser("list", help="List installed skills")

    # skill scan
    scan_p = skill_sub.add_parser("scan", help="Scan a skill file for safety")
    scan_p.add_argument("path", help="Path to SKILL.md file")

    # skill remove
    remove_p = skill_sub.add_parser("remove", help="Remove an installed skill")
    remove_p.add_argument("name", help="Skill name to remove")

    # skill info
    info_p = skill_sub.add_parser("info", help="Show skill details")
    info_p.add_argument("name", help="Skill name")

    # skill discover
    discover_p = skill_sub.add_parser("discover", help="Discover skills from the network")
    discover_p.add_argument("--query", "-q", help="Search query")
    discover_p.add_argument("--tag", "-t", help="Filter by tag")
    discover_p.add_argument("--limit", "-n", type=int, default=10, help="Max results")

    # --- parse ---
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "skill":
        if args.skill_action == "install":
            install_skill(args.source, force=args.force)
        elif args.skill_action == "list":
            list_skills()
        elif args.skill_action == "scan":
            scan_skill(args.path)
        elif args.skill_action == "remove":
            remove_skill(args.name)
        elif args.skill_action == "info":
            skill_info(args.name)
        elif args.skill_action == "discover":
            discover_skills(query=args.query, tag=args.tag, limit=args.limit)
        else:
            skill_parser.print_help()


if __name__ == "__main__":
    main()
