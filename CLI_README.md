# Agent-Self CLI — Agent Skill Manager

Install, discover, and manage SKILL.md files for your AI agent.

## Install

```bash
pip install agent-self
```

Or from source:
```bash
git clone https://github.com/yuroo-ui/Agent-Self.git
cd Agent-Self
pip install -e .
```

## Usage

### Install a skill from URL
```bash
agent-self skill install https://raw.githubusercontent.com/user/repo/main/SKILL.md
```

### Install from GitHub shorthand
```bash
agent-self skill install github:user/repo/SKILL.md
```

### Install from a local file
```bash
agent-self skill install ./path/to/SKILL.md
```

### List installed skills
```bash
agent-self skill list
```

### Discover skills from the network
```bash
agent-self skill discover --query "code review"
```

### Scan a skill for safety
```bash
agent-self skill scan ./path/to/SKILL.md
```

### Remove a skill
```bash
agent-self skill remove <skill-name>
```

### Show skill info
```bash
agent-self skill info <skill-name>
```

## Skill Directory

Skills are installed to `~/.agent-self/skills/`. Each skill is a folder:

```
~/.agent-self/skills/
├── code-reviewer/
│   ├── SKILL.md
│   └── meta.json
├── api-tester/
│   ├── SKILL.md
│   └── meta.json
```

## Security

Every skill is scanned before install:
- Permission audit (dangerous commands, file access patterns)
- Malware pattern detection
- Trust score calculation

Skills with trust score < 30 are blocked.
Skills with score 30-60 require `--force` flag.
