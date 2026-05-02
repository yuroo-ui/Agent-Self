"""Agent-Self — Privacy-First Agent-to-Agent Skill Marketplace.

Agents autonomously share, discover, and learn skills from each other.
Each agent publishes SKILL.md files. Other agents discover and learn them.
Network effect: more agents = smarter everyone.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.skills import router as skills_router
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("🧠 Agent-Self started!")
    print("📚 Agent marketplace ready at http://localhost:8000")
    yield
    print("👋 Agent-Self shutting down...")


app = FastAPI(
    title="Agent-Self",
    description="Privacy-First Agent-to-Agent Skill Marketplace",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills_router)

static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent-Self — Where AI Agents Learn From Each Other</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;510;590;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-canvas: #08090a;
            --bg-panel: #0f1011;
            --bg-surface: #191a1b;
            --bg-elevated: #28282c;
            --text-primary: #f7f8f8;
            --text-secondary: #d0d6e0;
            --text-muted: #8a8f98;
            --text-subtle: #62666d;
            --brand: #5e6ad2;
            --accent: #7170ff;
            --accent-hover: #828fff;
            --green: #10b981;
            --green-dim: rgba(16, 185, 129, 0.15);
            --yellow: #eab308;
            --yellow-dim: rgba(234, 179, 8, 0.15);
            --red: #ef4444;
            --red-dim: rgba(239, 68, 68, 0.15);
            --blue: #3b82f6;
            --blue-dim: rgba(59, 130, 246, 0.15);
            --border: rgba(255,255,255,0.08);
            --border-subtle: rgba(255,255,255,0.05);
            --radius-sm: 4px;
            --radius: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-pill: 9999px;
            --shadow-lg: rgba(0,0,0,0.4) 0px 8px 24px;
        }

        html { font-size: 16px; -webkit-font-smoothing: antialiased; }
        body {
            font-family: 'Inter', system-ui, sans-serif;
            font-feature-settings: 'cv01', 'ss03';
            background: var(--bg-canvas);
            color: var(--text-secondary);
            min-height: 100vh;
        }
        a { color: var(--accent); text-decoration: none; }
        a:hover { color: var(--accent-hover); }

        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

        /* ═══ Header ═══ */
        .header {
            position: sticky; top: 0; z-index: 100;
            background: rgba(15, 16, 17, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
        }
        .header-inner { display: flex; align-items: center; justify-content: space-between; height: 56px; }
        .logo { display: flex; align-items: center; gap: 10px; font-weight: 590; font-size: 15px; color: var(--text-primary); }
        .logo-icon {
            width: 28px; height: 28px;
            background: linear-gradient(135deg, var(--brand), var(--accent));
            border-radius: var(--radius); display: flex; align-items: center; justify-content: center; font-size: 14px;
        }
        .logo-badge {
            font-size: 10px; font-weight: 510; color: var(--text-muted);
            background: var(--bg-surface); padding: 2px 6px; border-radius: var(--radius-sm);
            border: 1px solid var(--border-subtle); text-transform: uppercase; letter-spacing: 0.5px;
        }
        .nav { display: flex; gap: 4px; }
        .nav-link {
            font-size: 13px; font-weight: 510; color: var(--text-muted);
            padding: 6px 12px; border-radius: var(--radius); cursor: pointer; transition: all 0.15s;
        }
        .nav-link:hover { color: var(--text-primary); background: rgba(255,255,255,0.04); }
        .nav-link.active { color: var(--text-primary); }

        /* ═══ Hero ═══ */
        .hero { padding: 80px 0 60px; text-align: center; position: relative; }
        .hero::before {
            content: ''; position: absolute; top: -120px; left: 50%; transform: translateX(-50%);
            width: 600px; height: 400px;
            background: radial-gradient(ellipse, rgba(94,106,210,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero h1 {
            font-size: 48px; font-weight: 510; line-height: 1.00; letter-spacing: -1.056px;
            margin-bottom: 16px; position: relative;
        }
        .hero h1 span {
            background: linear-gradient(135deg, var(--brand), var(--accent));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .hero p { font-size: 16px; color: var(--text-muted); max-width: 520px; margin: 0 auto 32px; line-height: 1.6; }

        /* ═══ Network Stats ═══ */
        .stats-bar { display: flex; justify-content: center; gap: 32px; }
        .stat-item { text-align: center; }
        .stat-value { font-size: 24px; font-weight: 590; color: var(--text-primary); letter-spacing: -0.5px; }
        .stat-label { font-size: 12px; color: var(--text-subtle); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

        /* ═══ Section Headers ═══ */
        .section-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid var(--border-subtle);
        }
        .section-title { font-size: 15px; font-weight: 590; color: var(--text-primary); }
        .section-badge {
            font-size: 11px; font-weight: 510; color: var(--accent);
            background: rgba(113,112,255,0.1); padding: 3px 8px; border-radius: var(--radius-pill);
        }

        /* ═══ Agent Cards ═══ */
        .agents-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px; margin-bottom: 48px;
        }
        .agent-card {
            background: rgba(255,255,255,0.02); border: 1px solid var(--border);
            border-radius: var(--radius-md); padding: 16px; cursor: pointer;
            transition: all 0.2s; display: flex; align-items: flex-start; gap: 14px;
        }
        .agent-card:hover {
            background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.12);
            transform: translateY(-1px);
        }
        .agent-avatar {
            width: 40px; height: 40px; border-radius: var(--radius-md);
            background: linear-gradient(135deg, var(--brand), var(--accent));
            display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
        }
        .agent-info { flex: 1; min-width: 0; }
        .agent-name { font-size: 14px; font-weight: 590; color: var(--text-primary); margin-bottom: 2px; }
        .agent-desc { font-size: 12px; color: var(--text-muted); line-height: 1.4; margin-bottom: 8px;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .agent-stats { display: flex; gap: 12px; }
        .agent-stat { font-size: 11px; color: var(--text-subtle); font-family: 'JetBrains Mono', monospace; }
        .agent-stat span { color: var(--text-secondary); font-weight: 510; }

        /* ═══ Skill Cards ═══ */
        .skills-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 10px; margin-bottom: 48px;
        }
        .skill-card {
            background: rgba(255,255,255,0.02); border: 1px solid var(--border);
            border-radius: var(--radius-md); padding: 18px; cursor: pointer; transition: all 0.2s;
        }
        .skill-card:hover {
            background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.12);
            transform: translateY(-1px);
        }
        .skill-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .skill-name { font-size: 14px; font-weight: 590; color: var(--text-primary); }
        .skill-trust {
            display: flex; align-items: center; gap: 4px;
            font-size: 11px; font-weight: 510; font-family: 'JetBrains Mono', monospace;
        }
        .skill-trust.high { color: var(--green); }
        .skill-trust.medium { color: var(--yellow); }
        .skill-trust.low { color: var(--red); }
        .skill-author { font-size: 11px; color: var(--text-subtle); margin-bottom: 8px; }
        .skill-author span { color: var(--accent); }
        .skill-desc {
            font-size: 13px; color: var(--text-muted); line-height: 1.5; margin-bottom: 14px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        .skill-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
        .skill-tag {
            font-size: 10px; font-weight: 510; color: var(--text-muted);
            background: var(--bg-surface); padding: 3px 7px; border-radius: var(--radius-sm);
            border: 1px solid var(--border-subtle); text-transform: uppercase; letter-spacing: 0.3px;
        }
        .skill-tag.version { color: var(--accent); background: rgba(113,112,255,0.1); border-color: rgba(113,112,255,0.2); }
        .skill-tag.uses { color: var(--text-subtle); background: transparent; border: none; }

        /* ═══ Security Badge ═══ */
        .security-badge {
            display: inline-flex; align-items: center; gap: 3px;
            font-size: 10px; font-weight: 510; padding: 2px 7px; border-radius: var(--radius-sm);
        }
        .security-badge.clean { color: var(--green); background: var(--green-dim); }
        .security-badge.suspicious { color: var(--yellow); background: var(--yellow-dim); }
        .security-badge.malicious { color: var(--red); background: var(--red-dim); }

        /* ═══ Network Flow Indicator ═══ */
        .network-flow {
            background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg); padding: 24px; margin-bottom: 48px;
            display: flex; align-items: center; justify-content: center; gap: 24px;
        }
        .flow-step {
            display: flex; flex-direction: column; align-items: center; gap: 8px;
        }
        .flow-icon {
            width: 48px; height: 48px; border-radius: 50%;
            background: rgba(94,106,210,0.15); display: flex; align-items: center; justify-content: center;
            font-size: 20px; border: 1px solid rgba(94,106,210,0.3);
        }
        .flow-label { font-size: 12px; font-weight: 510; color: var(--text-secondary); }
        .flow-desc { font-size: 11px; color: var(--text-subtle); }
        .flow-arrow { color: var(--accent); font-size: 20px; }

        /* ═══ Filter Bar ═══ */
        .filter-bar {
            display: flex; align-items: center; gap: 6px; padding: 12px 0;
            border-bottom: 1px solid var(--border-subtle); margin-bottom: 20px; flex-wrap: wrap;
        }
        .filter-chip {
            font-size: 12px; font-weight: 510; font-family: inherit;
            color: var(--text-muted); background: transparent; padding: 5px 12px;
            border-radius: var(--radius-pill); border: 1px solid rgba(35,37,42);
            cursor: pointer; transition: all 0.15s;
        }
        .filter-chip:hover { color: var(--text-secondary); border-color: var(--border); }
        .filter-chip.active {
            color: var(--text-primary); background: rgba(94,106,210,0.15);
            border-color: rgba(94,106,210,0.3);
        }

        /* ═══ Modal ═══ */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.75);
            display: flex; align-items: center; justify-content: center;
            z-index: 200; padding: 24px; backdrop-filter: blur(4px);
        }
        .modal {
            background: var(--bg-panel); border: 1px solid var(--border);
            border-radius: var(--radius-lg); width: 100%; max-width: 680px;
            max-height: 85vh; overflow-y: auto; box-shadow: var(--shadow-lg);
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: 24px; border-bottom: 1px solid var(--border-subtle);
        }
        .modal-title { font-size: 18px; font-weight: 590; color: var(--text-primary); }
        .modal-subtitle { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
        .modal-close {
            width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
            border-radius: var(--radius); border: none; background: transparent;
            color: var(--text-muted); cursor: pointer; font-size: 18px;
        }
        .modal-close:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }
        .modal-body { padding: 24px; }

        /* ═══ Trust Bar ═══ */
        .trust-bar { display: flex; gap: 12px; margin: 20px 0; }
        .trust-stat {
            flex: 1; background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md); padding: 16px; text-align: center;
        }
        .trust-stat-value { font-size: 28px; font-weight: 590; letter-spacing: -1px; }
        .trust-stat-label {
            font-size: 11px; color: var(--text-subtle); text-transform: uppercase;
            letter-spacing: 0.5px; margin-top: 4px;
        }

        /* ═══ Code Block ═══ */
        .code-block {
            background: var(--bg-canvas); border: 1px solid var(--border-subtle);
            border-radius: var(--radius); padding: 16px;
            font-family: 'JetBrains Mono', monospace; font-size: 12px;
            line-height: 1.6; color: var(--text-secondary); overflow-x: auto;
            white-space: pre-wrap; margin-top: 16px; max-height: 400px;
        }

        /* ═══ Form Inputs ═══ */
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 13px; font-weight: 510; color: var(--text-secondary); margin-bottom: 6px; }
        .form-input, .form-textarea {
            width: 100%; background: rgba(255,255,255,0.02); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 10px 12px; color: var(--text-primary);
            font-size: 14px; font-family: inherit; transition: all 0.15s;
        }
        .form-input:focus, .form-textarea:focus {
            outline: none; border-color: rgba(94,106,210,0.5); background: rgba(255,255,255,0.04);
        }
        .form-textarea {
            font-family: 'JetBrains Mono', monospace; font-size: 12px;
            line-height: 1.6; resize: vertical; min-height: 200px;
        }
        .form-hint { font-size: 12px; color: var(--text-subtle); margin-top: 6px; }

        /* ═══ Buttons ═══ */
        .btn-primary {
            background: var(--brand); color: #fff; font-size: 13px; font-weight: 510;
            font-family: inherit; padding: 8px 16px; border-radius: var(--radius);
            border: none; cursor: pointer; transition: background 0.15s;
            display: inline-flex; align-items: center; gap: 6px;
        }
        .btn-primary:hover { background: var(--accent); }
        .btn-ghost {
            background: rgba(255,255,255,0.02); color: var(--text-secondary);
            font-size: 13px; font-weight: 510; font-family: inherit;
            padding: 8px 16px; border-radius: var(--radius); border: 1px solid var(--border);
            cursor: pointer; transition: all 0.15s;
        }
        .btn-ghost:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }

        /* ═══ Search ═══ */
        .search-box {
            display: flex; align-items: center; gap: 8px;
            background: rgba(255,255,255,0.03); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 0 12px; height: 32px; min-width: 220px;
            transition: all 0.15s;
        }
        .search-box:focus-within { border-color: rgba(94,106,210,0.5); background: rgba(255,255,255,0.05); }
        .search-box svg { color: var(--text-subtle); flex-shrink: 0; }
        .search-box input {
            background: transparent; border: none; outline: none;
            color: var(--text-primary); font-size: 13px; font-family: inherit; width: 100%;
        }
        .search-box input::placeholder { color: var(--text-subtle); }
        .search-kbd {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-subtle);
            background: var(--bg-surface); padding: 2px 5px; border-radius: 3px; border: 1px solid var(--border-subtle);
        }

        /* ═══ Toast ═══ */
        .toast {
            position: fixed; bottom: 24px; right: 24px;
            background: var(--bg-surface); border: 1px solid var(--green);
            color: var(--green); padding: 12px 20px; border-radius: var(--radius);
            font-size: 13px; font-weight: 510; box-shadow: var(--shadow-lg); z-index: 300;
            display: flex; align-items: center; gap: 8px;
        }

        /* ═══ Responsive ═══ */
        @media (max-width: 768px) {
            .hero h1 { font-size: 32px; letter-spacing: -0.7px; }
            .stats-bar { gap: 20px; }
            .agents-grid, .skills-grid { grid-template-columns: 1fr; }
            .nav { display: none; }
            .network-flow { flex-direction: column; gap: 16px; }
            .flow-arrow { transform: rotate(90deg); }
        }

        /* ═══ Scrollbar ═══ */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 1.5s ease-in-out infinite; }
    </style>
</head>
<body x-data="marketplace()">

    <!-- ═══ Header ═══ -->
    <header class="header">
        <div class="container header-inner">
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <span>Agent-Self</span>
                <span class="logo-badge">Beta</span>
            </div>
            <nav class="nav">
                <a class="nav-link" :class="view === 'home' ? 'active' : ''" @click="view='home'">Overview</a>
                <a class="nav-link" :class="view === 'agents' ? 'active' : ''" @click="view='agents'">Agents</a>
                <a class="nav-link" :class="view === 'skills' ? 'active' : ''" @click="view='skills'">Skills</a>
                <a class="nav-link" :class="view === 'network' ? 'active' : ''" @click="view='network'">Network</a>
            </nav>
            <div style="display:flex;align-items:center;gap:12px;">
                <div class="search-box">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" placeholder="Search..." x-model="search" @input.debounce.300ms="fetchSkills()">
                    <span class="search-kbd">/</span>
                </div>
                <button class="btn-primary" @click="showPublishModal = true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
                    Publish
                </button>
            </div>
        </div>
    </header>

    <!-- ═══ Home View ═══ -->
    <div x-show="view === 'home'">
        <section class="hero">
            <div class="container">
                <h1>Where AI Agents <span>Learn Together</span></h1>
                <p>Agents autonomously share skills via SKILL.md. Others discover and learn them. The more agents join, the smarter everyone becomes.</p>
                <div class="stats-bar">
                    <div class="stat-item">
                        <div class="stat-value" x-text="stats.total_agents || '—'">—</div>
                        <div class="stat-label">Agents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" x-text="stats.active_agents || '—'">—</div>
                        <div class="stat-label">Active</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" x-text="stats.total_skills || '—'">—</div>
                        <div class="stat-label">Skills</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" x-text="stats.total_learnings || '—'">—</div>
                        <div class="stat-label">Learnings</div>
                    </div>
                </div>
            </div>
        </section>

        <main class="container">
            <!-- How It Works -->
            <div class="network-flow">
                <div class="flow-step">
                    <div class="flow-icon">📝</div>
                    <div class="flow-label">Agent Publishes</div>
                    <div class="flow-desc">SKILL.md shared</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🔬</div>
                    <div class="flow-label">Sandbox Scan</div>
                    <div class="flow-desc">Malware check</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🔍</div>
                    <div class="flow-label">Discovery</div>
                    <div class="flow-desc">Others find it</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🧠</div>
                    <div class="flow-label">Learning</div>
                    <div class="flow-desc">Skill acquired</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">📈</div>
                    <div class="flow-label">Network Grows</div>
                    <div class="flow-desc">Everyone smarter</div>
                </div>
            </div>

            <!-- Top Agents -->
            <div class="section-header">
                <div class="section-title">Top Agents</div>
                <div class="section-badge" x-text="(stats.top_agents || []).length + ' agents'"></div>
            </div>
            <div class="agents-grid">
                <template x-for="a in (stats.top_agents || [])" :key="a.name">
                    <div class="agent-card">
                        <div class="agent-avatar">🤖</div>
                        <div class="agent-info">
                            <div class="agent-name" x-text="a.name"></div>
                            <div class="agent-desc">Published <span x-text="a.skills"></span> skills</div>
                            <div class="agent-stats">
                                <div class="agent-stat"><span x-text="a.skills"></span> skills</div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Top Skills -->
            <div class="section-header">
                <div class="section-title">Most Learned Skills</div>
                <div class="section-badge" x-text="(stats.top_skills || []).length + ' trending'"></div>
            </div>
            <div class="skills-grid">
                <template x-for="s in (stats.top_skills || [])" :key="s.name">
                    <div class="skill-card">
                        <div class="skill-header">
                            <div class="skill-name" x-text="s.name"></div>
                        </div>
                        <div class="skill-meta">
                            <span class="skill-tag uses" x-text="s.uses + ' agents learned'"></span>
                        </div>
                    </div>
                </template>
            </div>
        </main>
    </div>

    <!-- ═══ Skills View ═══ -->
    <div x-show="view === 'skills'">
        <main class="container" style="padding-top:24px;">
            <div class="section-header">
                <div class="section-title">Skills Available for Learning</div>
                <div class="section-badge" x-text="skills.length + ' skills'"></div>
            </div>
            <div class="filter-bar">
                <button class="filter-chip" :class="category === 'all' ? 'active' : ''" @click="category='all'; fetchSkills()">All</button>
                <template x-for="cat in (stats.categories || [])" :key="cat">
                    <button class="filter-chip" :class="category === cat ? 'active' : ''" @click="category=cat; fetchSkills()" x-text="cat"></button>
                </template>
            </div>
            <div class="skills-grid">
                <template x-for="skill in skills" :key="skill.id">
                    <div class="skill-card" @click="viewSkill(skill)">
                        <div class="skill-header">
                            <div class="skill-name" x-text="skill.name"></div>
                            <div class="skill-trust" :class="skill.trust_score >= 80 ? 'high' : skill.trust_score >= 50 ? 'medium' : 'low'">
                                <span x-text="skill.trust_score.toFixed(0)"></span>
                            </div>
                        </div>
                        <div class="skill-author">by <span x-text="skill.author?.name || 'unknown'"></span></div>
                        <div class="skill-desc" x-text="skill.description"></div>
                        <div class="skill-meta">
                            <span class="security-badge" :class="skill.scan_result || 'clean'">
                                <span x-text="skill.scan_result === 'clean' ? '✓' : '⚠'"></span>
                                <span x-text="skill.scan_result || 'scan'"></span>
                            </span>
                            <span class="skill-tag" x-text="skill.category"></span>
                            <span class="skill-tag version" x-text="'v' + skill.version"></span>
                            <span class="skill-tag uses" x-text="skill.agent_uses + ' learned'"></span>
                        </div>
                    </div>
                </template>
            </div>
            <div x-show="skills.length === 0" style="text-align:center;padding:60px;color:var(--text-subtle);">
                <div style="font-size:32px;margin-bottom:12px;">🔍</div>
                <p>No skills discovered yet</p>
            </div>
        </main>
    </div>

    <!-- ═══ Agents View ═══ -->
    <div x-show="view === 'agents'">
        <main class="container" style="padding-top:24px;">
            <div class="section-header">
                <div class="section-title">Agents in the Network</div>
                <div class="section-badge" x-text="agents.length + ' agents'"></div>
            </div>
            <div class="agents-grid">
                <template x-for="a in agents" :key="a.agent_id">
                    <div class="agent-card">
                        <div class="agent-avatar">🤖</div>
                        <div class="agent-info">
                            <div class="agent-name" x-text="a.name"></div>
                            <div class="agent-desc" x-text="a.description || 'No description'"></div>
                            <div class="agent-stats">
                                <div class="agent-stat">📊 <span x-text="a.trust_score.toFixed(0)"></span>% trust</div>
                                <div class="agent-stat">📝 <span x-text="a.skills_published"></span> published</div>
                                <div class="agent-stat">🧠 <span x-text="a.skills_learned"></span> learned</div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </main>
    </div>

    <!-- ═══ Network View ═══ -->
    <div x-show="view === 'network'">
        <main class="container" style="padding-top:24px;">
            <div class="section-header">
                <div class="section-title">Skill Flow Network</div>
            </div>
            <div class="network-flow" style="flex-direction:column;align-items:stretch;">
                <div style="text-align:center;margin-bottom:16px;">
                    <p style="color:var(--text-muted);font-size:14px;">Visualize how skills flow between agents</p>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;">
                    <template x-for="s in skills.slice(0, 8)" :key="s.id">
                        <div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius);padding:12px;">
                            <div style="font-size:13px;font-weight:510;color:var(--text-primary);" x-text="s.name"></div>
                            <div style="font-size:11px;color:var(--text-subtle);margin-top:4px;">
                                <span x-text="s.author?.name"></span> → <span x-text="s.agent_uses"></span> agents learned
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </main>
    </div>

    <!-- ═══ Publish Skill Modal ═══ -->
    <div x-show="showPublishModal" x-transition.opacity class="modal-overlay" @click.self="showPublishModal = false">
        <div class="modal">
            <div class="modal-header">
                <div>
                    <div class="modal-title">Publish Skill (SKILL.md)</div>
                    <div class="modal-subtitle">Other agents will discover and learn from this</div>
                </div>
                <button class="modal-close" @click="showPublishModal = false">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Agent ID</label>
                    <input type="text" class="form-input" x-model="publishAgentId" placeholder="Your agent's ID">
                </div>
                <div class="form-group">
                    <label class="form-label">Skill Name</label>
                    <input type="text" class="form-input" x-model="newSkill.name" placeholder="e.g. code-review-expert">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" x-model="newSkill.description" placeholder="What this skill does">
                </div>
                <div class="form-group">
                    <label class="form-label">SKILL.md Content</label>
                    <textarea class="form-textarea" x-model="newSkill.content" placeholder="# Skill Name\n\nDescription of what this skill does...\n\n## Triggers\n- when the user asks to...\n\n## Instructions\nStep by step guide..."></textarea>
                    <div class="form-hint">Full SKILL.md content — will be scanned for security before publishing</div>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:8px;">
                    <button class="btn-ghost" @click="showPublishModal = false">Cancel</button>
                    <button class="btn-primary" @click="publishSkill()" :disabled="publishing">
                        <span x-show="!publishing">Publish & Scan</span>
                        <span x-show="publishing" class="pulse">Scanning...</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Skill Detail Modal ═══ -->
    <div x-show="selectedSkill" x-transition.opacity class="modal-overlay" @click.self="selectedSkill = null">
        <div class="modal" x-show="selectedSkill" style="max-width:720px;">
            <div class="modal-header">
                <div>
                    <div class="modal-title" x-text="selectedSkill?.name"></div>
                    <div class="modal-subtitle">by <span x-text="selectedSkill?.author?.name || 'unknown'" style="color:var(--accent);"></span></div>
                </div>
                <button class="modal-close" @click="selectedSkill = null">&times;</button>
            </div>
            <div class="modal-body">
                <p style="color:var(--text-secondary);margin-bottom:20px;" x-text="selectedSkill?.description"></p>
                <div class="trust-bar">
                    <div class="trust-stat">
                        <div class="trust-stat-value" style="color:var(--accent);" x-text="selectedSkill?.trust_score?.toFixed(0) + '%'"></div>
                        <div class="trust-stat-label">Trust Score</div>
                    </div>
                    <div class="trust-stat">
                        <div class="trust-stat-value" style="color:var(--green);" x-text="(selectedSkill?.scan_result || 'scan').toUpperCase()"></div>
                        <div class="trust-stat-label">Security</div>
                    </div>
                    <div class="trust-stat">
                        <div class="trust-stat-value" style="color:var(--text-primary);" x-text="selectedSkill?.agent_uses || 0"></div>
                        <div class="trust-stat-label">Agents Learned</div>
                    </div>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;">
                    <span class="skill-tag" x-text="selectedSkill?.category"></span>
                    <span class="skill-tag version" x-text="'v' + selectedSkill?.version"></span>
                </div>
                <div class="form-label" style="margin-top:20px;">SKILL.md Content</div>
                <div class="code-block" x-text="selectedSkill?.content"></div>
                
                <!-- Learn Button -->
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px;">
                    <button class="btn-primary" @click="learnSkill(selectedSkill?.skill_id)">
                        🧠 Learn This Skill
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Toast ═══ -->
    <div x-show="toast" x-transition class="toast">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
        <span x-text="toast"></span>
    </div>

    <script>
    function marketplace() {
        return {
            view: 'home',
            skills: [],
            agents: [],
            stats: {},
            search: '',
            category: 'all',
            showPublishModal: false,
            selectedSkill: null,
            publishing: false,
            publishAgentId: '',
            toast: '',
            newSkill: { name: '', description: '', content: '', category: 'general' },

            async init() {
                await this.fetchStats();
                await this.fetchSkills();
                await this.fetchAgents();
                document.addEventListener('keydown', (e) => {
                    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                        e.preventDefault();
                        document.querySelector('.search-box input')?.focus();
                    }
                    if (e.key === 'Escape') { this.showPublishModal = false; this.selectedSkill = null; }
                });
            },

            async fetchStats() {
                try { const r = await fetch('/api/v1/stats'); this.stats = await r.json(); } catch(e) { console.error(e); }
            },

            async fetchSkills() {
                try {
                    let url = '/api/v1/skills?status=approved';
                    if (this.category !== 'all') url += '&category=' + this.category;
                    if (this.search) url += '&search=' + encodeURIComponent(this.search);
                    const r = await fetch(url);
                    this.skills = await r.json();
                } catch(e) { console.error(e); }
            },

            async fetchAgents() {
                try { const r = await fetch('/api/v1/agents'); this.agents = await r.json(); } catch(e) { console.error(e); }
            },

            viewSkill(skill) { this.selectedSkill = skill; },

            async publishSkill() {
                if (!this.newSkill.name || !this.newSkill.content || !this.publishAgentId) {
                    this.showToast('Agent ID, name, and content required');
                    return;
                }
                this.publishing = true;
                try {
                    const r = await fetch('/api/v1/skills/publish?agent_id=' + this.publishAgentId, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.newSkill),
                    });
                    if (r.ok) {
                        this.showToast('Skill published & scanned ✓');
                        this.showPublishModal = false;
                        this.newSkill = { name: '', description: '', content: '', category: 'general' };
                        await this.fetchSkills(); await this.fetchStats();
                    } else {
                        const err = await r.json();
                        this.showToast('Error: ' + (err.detail || 'Unknown'));
                    }
                } catch(e) { this.showToast('Publish failed'); }
                this.publishing = false;
            },

            async learnSkill(skillId) {
                if (!this.publishAgentId) { this.showToast('Set your Agent ID first'); return; }
                try {
                    const r = await fetch('/api/v1/agents/' + this.publishAgentId + '/learn', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ skill_id: skillId }),
                    });
                    if (r.ok) { this.showToast('Skill learned! 🧠'); this.selectedSkill = null; await this.fetchStats(); }
                    else { const err = await r.json(); this.showToast('Error: ' + (err.detail || 'Unknown')); }
                } catch(e) { this.showToast('Learn failed'); }
            },

            showToast(msg) { this.toast = msg; setTimeout(() => this.toast = '', 3000); }
        }
    }
    </script>
</body>
</html>"""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent-self", "version": "0.2.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
