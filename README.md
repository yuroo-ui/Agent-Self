# 🧠 Agent-Self

**Privacy-First Skill Marketplace for AI Agents**

> Agents learn from each other, skills get smarter, privacy stays intact.

## ✨ Why Agent-Self?

```
┌─────────────────────────────────────────────────────┐
│  Agent-Self Marketplace                             │
│                                                     │
│  🔒 Privacy-First    Skills scanned before reach    │
│                      your agent                     │
│                                                     │
│  🧠 Learn Together   Collective intelligence        │
│                      agents improve each other      │
│                                                     │
│  🛡️ Trust System     Verified skills, immutable     │
│                      versions, full audit trail     │
│                                                     │
│  🔐 No Malware       Sandboxed execution,           │
│                      auto-scan on publish           │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/yuroo-ui/Agent-Self.git
cd Agent-Self

# Install
pip install -r requirements.txt

# Run
python -m app.main

# Open browser
http://localhost:8000
```

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Web UI     │───▶│   API Server │───▶│   Sandbox    │
│  (Frontend)  │    │   (FastAPI)  │    │  (Scanner)   │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  Database    │
                    │ (PostgreSQL) │
                    └──────────────┘
```

## 📦 Features

### For Skill Developers
- ✅ Submit skills to marketplace
- ✅ Version tracking & changelog
- ✅ Build reputation through usage
- ✅ Immutable publish (no retroactive edits)

### For Agent Users
- ✅ Browse & discover trusted skills
- ✅ Automatic security scanning
- ✅ Trust score & community reviews
- ✅ Federated learning (privacy-preserving)

### Security
- ✅ Sandboxed skill execution
- ✅ Static analysis (malware detection)
- ✅ Dynamic analysis (runtime behavior)
- ✅ Network monitoring (data exfiltration detection)
- ✅ Permission audit

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + FastAPI |
| Frontend | HTML + Alpine.js + Tailwind |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Sandbox | Docker / Firecracker |
| Search | Full-text search |
| Auth | JWT + API keys |

## 📁 Project Structure

```
Agent-Self/
├── app/
│   ├── api/            # API routes
│   ├── models/         # Database models
│   ├── services/       # Business logic
│   ├── sandbox/        # Skill scanner
│   └── web/            # Frontend templates
├── skills/             # Approved skills
├── tests/              # Test suite
├── docker/             # Docker configs
└── docs/               # Documentation
```

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Submit PR
4. Skills reviewed before merge

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**Built with ❤️ for AI agents who want to learn together.**
