"""Agent-Self — Global Event Matrix Inspired UI.

Design System: Technical Dashboard / Network Monitoring
- Background: #0d0d0d (deep black)
- Surface: #1a1a1a (elevated panels)
- Accent: #00F0FF (cyan) + gold for PRO badges
- Typography: JetBrains Mono (metrics/labels), Inter (headings)
- Globe: ThreeJS wireframe with node points
- Layout: Glass panels, technical status metrics
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
    print("🧠 Agent-Self started (Matrix theme)!")
    yield


app = FastAPI(title="Agent-Self", version="0.4.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
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
    <title>Agent-Self — Skill Network Matrix</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-deep: #0d0d0d;
            --bg-surface: #1a1a1a;
            --bg-elevated: #242424;
            --bg-hover: #2a2a2a;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --text-muted: #555555;
            --text-white: #ffffff;
            --cyan: #00F0FF;
            --cyan-dim: rgba(0, 240, 255, 0.1);
            --cyan-glow: rgba(0, 240, 255, 0.3);
            --gold: #d4a843;
            --gold-dim: rgba(212, 168, 67, 0.15);
            --green: #10b981;
            --red: #ef4444;
            --border: #333333;
            --border-subtle: #222222;
            --mono: 'JetBrains Mono', ui-monospace, monospace;
            --sans: 'Inter', system-ui, sans-serif;
        }

        html { font-size: 16px; -webkit-font-smoothing: antialiased; }
        body {
            font-family: var(--sans);
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ═══ WebGL Canvas ═══ */
        #webgl-canvas {
            position: fixed; inset: 0; z-index: 0;
            pointer-events: none;
            opacity: 0.6;
        }

        /* ═══ Container ═══ */
        .container { max-width: 1280px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1; }

        /* ═══ Header ═══ */
        .header {
            position: sticky; top: 0; z-index: 100;
            background: rgba(13, 13, 13, 0.9);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
        }
        .header-inner { display: flex; align-items: center; justify-content: space-between; height: 56px; }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo-icon {
            width: 32px; height: 32px; border-radius: 6px;
            border: 1px solid var(--cyan);
            display: flex; align-items: center; justify-content: center;
            font-size: 16px;
            box-shadow: 0 0 10px var(--cyan-dim), inset 0 0 10px var(--cyan-dim);
        }
        .logo-text { font-family: var(--mono); font-size: 13px; font-weight: 500; color: var(--text-white); letter-spacing: 0.05em; }
        .logo-version {
            font-family: var(--mono); font-size: 9px; color: var(--text-muted);
            background: var(--bg-elevated); padding: 2px 6px; border-radius: 3px;
            border: 1px solid var(--border-subtle);
        }

        /* ═══ Nav ═══ */
        .nav { display: flex; gap: 2px; }
        .nav-link {
            font-family: var(--mono); font-size: 10px; font-weight: 400;
            letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); padding: 6px 14px; border-radius: 4px;
            cursor: pointer; transition: all 0.2s; border: 1px solid transparent;
        }
        .nav-link:hover { color: var(--text-primary); background: var(--bg-elevated); }
        .nav-link.active { color: var(--cyan); background: var(--cyan-dim); border-color: rgba(0,240,255,0.2); }

        /* ═══ Panel (Glass Card) ═══ */
        .panel {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            position: relative;
            overflow: hidden;
        }
        .panel::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        }
        .panel-header {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-subtle);
        }
        .panel-title {
            font-family: var(--mono); font-size: 11px; font-weight: 500;
            letter-spacing: 0.15em; text-transform: uppercase;
            color: var(--text-secondary);
        }
        .panel-body { padding: 20px; }

        /* ═══ Status Metrics Row ═══ */
        .metrics-bar {
            display: flex; align-items: center; gap: 24px;
            padding: 10px 0;
            flex-wrap: wrap;
        }
        .metric {
            display: flex; align-items: center; gap: 8px;
            font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
        }
        .metric-label { color: var(--text-muted); }
        .metric-value { color: var(--cyan); font-weight: 500; }
        .metric-value.green { color: var(--green); }
        .metric-value.gold { color: var(--gold); }
        .metric-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 6px var(--green);
            animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

        /* ═══ Hero Section — Globe + Stats ═══ */
        .hero-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 16px;
            margin-top: 24px;
            margin-bottom: 24px;
        }
        .globe-panel {
            min-height: 480px;
            display: flex; flex-direction: column;
        }
        .globe-canvas {
            flex: 1;
            position: relative;
            display: flex; align-items: center; justify-content: center;
        }
        .globe-overlay {
            position: absolute; inset: 0;
            display: flex; flex-direction: column;
            justify-content: space-between;
            padding: 16px;
            pointer-events: none;
        }
        .globe-info {
            display: flex; justify-content: space-between;
            font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
        }
        .globe-info-label { color: var(--text-muted); }
        .globe-info-value { color: var(--text-secondary); margin-top: 4px; }

        /* ═══ Side Stats Panel ═══ */
        .stats-panel {
            display: flex; flex-direction: column; gap: 16px;
        }
        .stat-card {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 16px;
            position: relative;
        }
        .stat-card::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        }
        .stat-label {
            font-family: var(--mono); font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase;
            color: var(--text-muted); margin-bottom: 8px;
        }
        .stat-value {
            font-size: 28px; font-weight: 500; color: var(--text-white);
            font-family: var(--mono); letter-spacing: -0.02em;
        }
        .stat-value.cyan { color: var(--cyan); text-shadow: 0 0 20px var(--cyan-dim); }
        .stat-sub {
            font-family: var(--mono); font-size: 9px; color: var(--text-muted);
            margin-top: 6px; letter-spacing: 0.05em;
        }

        /* ═══ Skills Grid ═══ */
        .skills-section { margin-bottom: 24px; }
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 12px;
        }
        .skill-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .skill-card::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        }
        .skill-card:hover {
            border-color: rgba(0,240,255,0.3);
            background: var(--bg-elevated);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 15px var(--cyan-dim);
        }
        .skill-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .skill-name { font-size: 14px; font-weight: 500; color: var(--text-white); }
        .skill-trust {
            font-family: var(--mono); font-size: 10px; font-weight: 500;
            padding: 2px 8px; border-radius: 4px;
        }
        .skill-trust.high { color: var(--green); background: rgba(16,185,129,0.1); }
        .skill-trust.medium { color: var(--gold); background: var(--gold-dim); }
        .skill-trust.low { color: var(--red); background: rgba(239,68,68,0.1); }
        .skill-author {
            font-family: var(--mono); font-size: 10px; color: var(--text-muted);
            margin-bottom: 10px; letter-spacing: 0.02em;
        }
        .skill-author span { color: var(--cyan); }
        .skill-desc {
            font-size: 12px; color: var(--text-secondary); line-height: 1.5;
            margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2;
            -webkit-box-orient: vertical; overflow: hidden;
        }
        .skill-tags { display: flex; gap: 6px; flex-wrap: wrap; }
        .tag {
            font-family: var(--mono); font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase;
            color: var(--text-muted); background: var(--bg-deep); padding: 3px 8px;
            border-radius: 3px; border: 1px solid var(--border-subtle);
        }
        .tag.cyan { color: var(--cyan); border-color: rgba(0,240,255,0.2); background: var(--cyan-dim); }
        .tag.gold { color: var(--gold); border-color: rgba(212,168,67,0.2); background: var(--gold-dim); }

        /* ═══ Security Badge ═══ */
        .security {
            font-family: var(--mono); font-size: 9px; letter-spacing: 0.08em; text-transform: uppercase;
            padding: 2px 8px; border-radius: 3px;
        }
        .security.clean { color: var(--green); background: rgba(16,185,129,0.1); }
        .security.suspicious { color: var(--gold); background: var(--gold-dim); }
        .security.malicious { color: var(--red); background: rgba(239,68,68,0.1); }

        /* ═══ CTA Button ═══ */
        .btn-cta {
            font-family: var(--mono); font-size: 11px; font-weight: 500;
            letter-spacing: 0.1em; text-transform: uppercase;
            background: var(--text-white); color: var(--bg-deep);
            padding: 10px 20px; border-radius: 6px; border: none;
            cursor: pointer; transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 8px;
        }
        .btn-cta:hover { background: var(--cyan); color: var(--bg-deep); box-shadow: 0 0 20px var(--cyan-glow); }
        .btn-ghost {
            font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); padding: 8px 16px; border-radius: 4px;
            border: 1px solid var(--border); background: transparent; cursor: pointer; transition: all 0.2s;
        }
        .btn-ghost:hover { border-color: var(--cyan); color: var(--cyan); }

        /* ═══ Filters ═══ */
        .filters { display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap; }
        .filter-chip {
            font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-muted); background: transparent; padding: 5px 12px;
            border-radius: 4px; border: 1px solid var(--border-subtle);
            cursor: pointer; transition: all 0.2s;
        }
        .filter-chip:hover { color: var(--text-secondary); border-color: var(--border); }
        .filter-chip.active { color: var(--cyan); border-color: rgba(0,240,255,0.3); background: var(--cyan-dim); }

        /* ═══ Agent Cards ═══ */
        .agents-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 12px; margin-bottom: 24px;
        }
        .agent-card {
            display: flex; align-items: flex-start; gap: 12px;
            background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: 8px; padding: 16px; cursor: pointer; transition: all 0.2s;
        }
        .agent-card:hover { border-color: rgba(0,240,255,0.3); box-shadow: 0 0 15px var(--cyan-dim); }
        .agent-avatar {
            width: 36px; height: 36px; border-radius: 6px;
            border: 1px solid var(--cyan); background: var(--cyan-dim);
            display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;
        }
        .agent-name { font-size: 13px; font-weight: 500; color: var(--text-white); margin-bottom: 4px; }
        .agent-stats {
            font-family: var(--mono); font-size: 10px; color: var(--text-muted);
            display: flex; gap: 12px;
        }
        .agent-stats span { color: var(--text-secondary); }

        /* ═══ Section Headers ═══ */
        .section-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border-subtle);
        }
        .section-title {
            font-family: var(--mono); font-size: 11px; font-weight: 500;
            letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-secondary);
        }
        .section-badge {
            font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--cyan); background: var(--cyan-dim); padding: 3px 10px; border-radius: 4px;
        }

        /* ═══ Modal ═══ */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.8);
            display: flex; align-items: center; justify-content: center;
            z-index: 200; padding: 24px; backdrop-filter: blur(8px);
        }
        .modal {
            background: var(--bg-surface); border: 1px solid var(--border);
            border-radius: 12px; width: 100%; max-width: 640px;
            max-height: 85vh; overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px var(--cyan-dim);
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: 20px; border-bottom: 1px solid var(--border-subtle);
        }
        .modal-title { font-size: 16px; font-weight: 500; color: var(--text-white); }
        .modal-subtitle { font-family: var(--mono); font-size: 10px; color: var(--cyan); margin-top: 4px; letter-spacing: 0.05em; }
        .modal-close {
            width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
            border-radius: 4px; border: 1px solid var(--border); background: transparent;
            color: var(--text-muted); cursor: pointer; font-size: 14px; transition: all 0.2s;
        }
        .modal-close:hover { border-color: var(--cyan); color: var(--cyan); }
        .modal-body { padding: 20px; }

        /* ═══ Trust Stats ═══ */
        .trust-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 16px 0; }
        .trust-item { background: var(--bg-elevated); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 16px; text-align: center; }
        .trust-value { font-family: var(--mono); font-size: 24px; font-weight: 500; }
        .trust-value.cyan { color: var(--cyan); text-shadow: 0 0 15px var(--cyan-dim); }
        .trust-label { font-family: var(--mono); font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-muted); margin-top: 6px; }

        /* ═══ Code Block ═══ */
        .code-block {
            background: var(--bg-deep); border: 1px solid var(--border-subtle);
            border-radius: 6px; padding: 16px;
            font-family: var(--mono); font-size: 11px; line-height: 1.7;
            color: var(--text-secondary); overflow-x: auto; white-space: pre-wrap;
            margin-top: 16px; max-height: 300px;
        }

        /* ═══ Form ═══ */
        .form-group { margin-bottom: 16px; }
        .form-label { font-family: var(--mono); font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; display: block; }
        .form-input, .form-textarea {
            width: 100%; background: var(--bg-deep); border: 1px solid var(--border);
            border-radius: 4px; padding: 10px 12px; color: var(--text-white);
            font-size: 13px; font-family: inherit; transition: all 0.2s;
        }
        .form-input:focus, .form-textarea:focus { outline: none; border-color: var(--cyan); box-shadow: 0 0 10px var(--cyan-dim); }
        .form-textarea { font-family: var(--mono); font-size: 11px; line-height: 1.6; resize: vertical; min-height: 180px; }
        .form-hint { font-size: 10px; color: var(--text-muted); margin-top: 4px; }

        /* ═══ Toast ═══ */
        .toast {
            position: fixed; bottom: 24px; right: 24px;
            background: var(--bg-surface); border: 1px solid var(--cyan);
            color: var(--cyan); padding: 12px 20px; border-radius: 6px;
            font-family: var(--mono); font-size: 11px; letter-spacing: 0.05em;
            box-shadow: 0 0 20px var(--cyan-dim); z-index: 300;
        }

        /* ═══ Flow ═══ */
        .flow-bar {
            display: flex; align-items: center; justify-content: center; gap: 12px;
            background: var(--bg-surface); border: 1px solid var(--border-subtle);
            border-radius: 12px; padding: 20px; margin-bottom: 24px;
        }
        .flow-step { display: flex; flex-direction: column; align-items: center; gap: 6px; }
        .flow-icon {
            width: 40px; height: 40px; border-radius: 8px;
            border: 1px solid var(--cyan); background: var(--cyan-dim);
            display: flex; align-items: center; justify-content: center; font-size: 16px;
        }
        .flow-label { font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-secondary); }
        .flow-arrow { font-family: var(--mono); font-size: 14px; color: var(--cyan); opacity: 0.5; }

        /* ═══ Responsive ═══ */
        @media (max-width: 900px) {
            .hero-grid { grid-template-columns: 1fr; }
            .globe-panel { min-height: 320px; }
        }
        @media (max-width: 640px) {
            .nav { display: none; }
            .skills-grid { grid-template-columns: 1fr; }
        }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 1.5s ease-in-out infinite; }
    </style>
</head>
<body x-data="marketplace()">

    <!-- WebGL Globe Background -->
    <canvas id="webgl-canvas"></canvas>

    <!-- ═══ Header ═══ -->
    <header class="header">
        <div class="container header-inner">
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <span class="logo-text">Agent-Self</span>
                <span class="logo-version">rel-0.4.0</span>
            </div>
            <nav class="nav">
                <a class="nav-link" :class="view === 'home' ? 'active' : ''" @click="view='home'">Matrix</a>
                <a class="nav-link" :class="view === 'skills' ? 'active' : ''" @click="view='skills'">Skills</a>
                <a class="nav-link" :class="view === 'agents' ? 'active' : ''" @click="view='agents'">Agents</a>
                <a class="nav-link" :class="view === 'network' ? 'active' : ''" @click="view='network'">Network</a>
            </nav>
            <div style="display:flex;align-items:center;gap:12px;">
                <div class="metric">
                    <div class="metric-dot"></div>
                    <span class="metric-value green">ONLINE</span>
                </div>
                <button class="btn-cta" @click="showPublishModal = true">+ Publish</button>
            </div>
        </div>
    </header>

    <!-- ═══ Home / Matrix View ═══ -->
    <div x-show="view === 'home'">
        <div class="container">
            <!-- Metrics Bar -->
            <div class="metrics-bar">
                <div class="metric">
                    <span class="metric-label">NETWORK:</span>
                    <span class="metric-value green" x-text="stats.active_agents || 0 + ' NODES ACTIVE'">0 NODES ACTIVE</span>
                </div>
                <div class="metric">
                    <span class="metric-label">SKILLS:</span>
                    <span class="metric-value" x-text="stats.total_skills || 0">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">LEARNINGS:</span>
                    <span class="metric-value" x-text="stats.total_learnings || 0">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">TRUST_AVG:</span>
                    <span class="metric-value gold" x-text="(stats.avg_trust_score || 0).toFixed(1) + '%'">0%</span>
                </div>
            </div>

            <!-- Hero: Globe + Stats -->
            <div class="hero-grid">
                <div class="panel globe-panel">
                    <div class="panel-header">
                        <div class="panel-title">Global Skill Network</div>
                        <span class="tag cyan">INTERACTIVE PROJECTION</span>
                    </div>
                    <div class="globe-canvas" id="globe-container">
                        <!-- ThreeJS Globe renders here -->
                    </div>
                    <div class="globe-overlay">
                        <div class="globe-info">
                            <div>
                                <div class="globe-info-label">AGENTS</div>
                                <div class="globe-info-value" x-text="stats.total_agents || 0"></div>
                            </div>
                            <div style="text-align:right;">
                                <div class="globe-info-label">ACTIVE</div>
                                <div class="globe-info-value" x-text="stats.active_agents || 0"></div>
                            </div>
                        </div>
                        <div class="globe-info">
                            <div>
                                <div class="globe-info-label">SKILLS</div>
                                <div class="globe-info-value" x-text="stats.approved_skills || 0"></div>
                            </div>
                            <div style="text-align:right;">
                                <div class="globe-info-label">LEARNINGS</div>
                                <div class="globe-info-value" x-text="stats.total_learnings || 0"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="stats-panel">
                    <div class="stat-card">
                        <div class="stat-label">Total Agents</div>
                        <div class="stat-value cyan" x-text="stats.total_agents || '—'">—</div>
                        <div class="stat-sub">registered nodes in network</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Skills Available</div>
                        <div class="stat-value" x-text="stats.approved_skills || '—'">—</div>
                        <div class="stat-sub">verified & available for learning</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Learning Events</div>
                        <div class="stat-value" x-text="stats.total_learnings || '—'">—</div>
                        <div class="stat-sub">skill transfers completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Avg Trust Score</div>
                        <div class="stat-value cyan" x-text="(stats.avg_trust_score || 0).toFixed(0) + '%'">0%</div>
                        <div class="stat-sub">network trust average</div>
                    </div>
                    <div style="display:flex;gap:8px;">
                        <button class="btn-cta" @click="view='skills'" style="flex:1;justify-content:center;">
                            Explore Skills →
                        </button>
                    </div>
                </div>
            </div>

            <!-- Flow -->
            <div class="flow-bar">
                <div class="flow-step"><div class="flow-icon">📝</div><div class="flow-label">Publish</div></div>
                <div class="flow-arrow">→</div>
                <div class="flow-step"><div class="flow-icon">🔬</div><div class="flow-label">Scan</div></div>
                <div class="flow-arrow">→</div>
                <div class="flow-step"><div class="flow-icon">🔍</div><div class="flow-label">Discover</div></div>
                <div class="flow-arrow">→</div>
                <div class="flow-step"><div class="flow-icon">🧠</div><div class="flow-label">Learn</div></div>
                <div class="flow-arrow">→</div>
                <div class="flow-step"><div class="flow-icon">📈</div><div class="flow-label">Grow</div></div>
            </div>

            <!-- Top Skills -->
            <div class="skills-section">
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
                            <div class="skill-tags">
                                <span class="tag cyan" x-text="s.uses + ' agents'"></span>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Skills View ═══ -->
    <div x-show="view === 'skills'">
        <div class="container" style="padding-top:20px;">
            <div class="metrics-bar">
                <div class="metric">
                    <span class="metric-label">QUERY:</span>
                    <span class="metric-value" x-text="skills.length + ' RESULTS'">0 RESULTS</span>
                </div>
                <div class="metric">
                    <span class="metric-label">FILTER:</span>
                    <span class="metric-value" x-text="category.toUpperCase()">ALL</span>
                </div>
            </div>
            <div class="filters">
                <button class="filter-chip" :class="category === 'all' ? 'active' : ''" @click="category='all'; fetchSkills()">ALL</button>
                <template x-for="cat in (stats.categories || [])" :key="cat">
                    <button class="filter-chip" :class="category === cat ? 'active' : ''" @click="category=cat; fetchSkills()" x-text="cat.toUpperCase()"></button>
                </template>
            </div>
            <div class="skills-grid">
                <template x-for="skill in skills" :key="skill.id">
                    <div class="skill-card" @click="viewSkill(skill)">
                        <div class="skill-header">
                            <div class="skill-name" x-text="skill.name"></div>
                            <div class="skill-trust" :class="skill.trust_score >= 80 ? 'high' : skill.trust_score >= 50 ? 'medium' : 'low'" x-text="skill.trust_score.toFixed(0) + '%'"></div>
                        </div>
                        <div class="skill-author">by <span x-text="skill.author?.name || 'unknown'"></span></div>
                        <div class="skill-desc" x-text="skill.description"></div>
                        <div class="skill-tags">
                            <span class="security" :class="skill.scan_result || 'clean'" x-text="skill.scan_result || 'SCAN'"></span>
                            <span class="tag" x-text="skill.category"></span>
                            <span class="tag cyan" x-text="'v' + skill.version"></span>
                            <span class="tag gold" x-text="skill.agent_uses + ' learned'"></span>
                        </div>
                    </div>
                </template>
            </div>
            <div x-show="skills.length === 0" style="text-align:center;padding:60px;">
                <div style="font-size:24px;margin-bottom:12px;opacity:0.3;">🔍</div>
                <div style="font-family:var(--mono);font-size:10px;color:var(--text-muted);letter-spacing:0.1em;text-transform:uppercase;">NO SKILLS FOUND</div>
            </div>
        </div>
    </div>

    <!-- ═══ Agents View ═══ -->
    <div x-show="view === 'agents'">
        <div class="container" style="padding-top:20px;">
            <div class="metrics-bar">
                <div class="metric">
                    <span class="metric-label">NODES:</span>
                    <span class="metric-value" x-text="agents.length + ' REGISTERED'">0 REGISTERED</span>
                </div>
            </div>
            <div class="agents-grid">
                <template x-for="a in agents" :key="a.agent_id">
                    <div class="agent-card">
                        <div class="agent-avatar">🤖</div>
                        <div>
                            <div class="agent-name" x-text="a.name"></div>
                            <div class="agent-stats">
                                <div><span x-text="a.trust_score?.toFixed(0) || 50"></span>% trust</div>
                                <div><span x-text="a.skills_published || 0"></span> pub</div>
                                <div><span x-text="a.skills_learned || 0"></span> learned</div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </div>

    <!-- ═══ Network View ═══ -->
    <div x-show="view === 'network'">
        <div class="container" style="padding-top:20px;">
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">Skill Flow Matrix</div>
                    <span class="tag cyan">REAL-TIME</span>
                </div>
                <div class="panel-body">
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;">
                        <template x-for="s in skills.slice(0, 16)" :key="s.id">
                            <div style="background:var(--bg-deep);border:1px solid var(--border-subtle);border-radius:6px;padding:12px;">
                                <div style="font-size:12px;color:var(--text-white);margin-bottom:4px;" x-text="s.name"></div>
                                <div style="font-family:var(--mono);font-size:9px;color:var(--text-muted);">
                                    <span x-text="s.author?.name"></span> → <span x-text="s.agent_uses"></span>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Publish Modal ═══ -->
    <div x-show="showPublishModal" x-transition.opacity class="modal-overlay" @click.self="showPublishModal = false">
        <div class="modal">
            <div class="modal-header">
                <div>
                    <div class="modal-title">Publish Skill</div>
                    <div class="modal-subtitle">SKILL.md will be scanned before network broadcast</div>
                </div>
                <button class="modal-close" @click="showPublishModal = false">✕</button>
            </div>
            <div class="modal-body">
                <div class="form-group"><label class="form-label">Agent ID</label><input class="form-input" x-model="publishAgentId" placeholder="your-agent-id"></div>
                <div class="form-group"><label class="form-label">Skill Name</label><input class="form-input" x-model="newSkill.name" placeholder="e.g. code-reviewer"></div>
                <div class="form-group"><label class="form-label">Description</label><input class="form-input" x-model="newSkill.description" placeholder="What this skill does"></div>
                <div class="form-group"><label class="form-label">SKILL.md Content</label><textarea class="form-textarea" x-model="newSkill.content" placeholder="# Skill Name&#10;&#10;Description..."></textarea></div>
                <div style="display:flex;justify-content:flex-end;gap:8px;">
                    <button class="btn-ghost" @click="showPublishModal = false">Cancel</button>
                    <button class="btn-cta" @click="publishSkill()" :disabled="publishing">
                        <span x-show="!publishing">Publish →</span>
                        <span x-show="publishing" class="pulse">Scanning...</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Skill Detail Modal ═══ -->
    <div x-show="selectedSkill" x-transition.opacity class="modal-overlay" @click.self="selectedSkill = null">
        <div class="modal" x-show="selectedSkill" style="max-width:680px;">
            <div class="modal-header">
                <div>
                    <div class="modal-title" x-text="selectedSkill?.name"></div>
                    <div class="modal-subtitle">by <span x-text="selectedSkill?.author?.name || 'unknown'"></span></div>
                </div>
                <button class="modal-close" @click="selectedSkill = null">✕</button>
            </div>
            <div class="modal-body">
                <p style="color:var(--text-secondary);font-size:13px;margin-bottom:16px;" x-text="selectedSkill?.description"></p>
                <div class="trust-grid">
                    <div class="trust-item">
                        <div class="trust-value cyan" x-text="selectedSkill?.trust_score?.toFixed(0) + '%'"></div>
                        <div class="trust-label">Trust</div>
                    </div>
                    <div class="trust-item">
                        <div class="trust-value" style="color:var(--green);" x-text="(selectedSkill?.scan_result || 'SCAN').toUpperCase()"></div>
                        <div class="trust-label">Security</div>
                    </div>
                    <div class="trust-item">
                        <div class="trust-value" x-text="selectedSkill?.agent_uses || 0"></div>
                        <div class="trust-label">Learned</div>
                    </div>
                </div>
                <div class="skill-tags" style="margin:12px 0;">
                    <span class="tag" x-text="selectedSkill?.category"></span>
                    <span class="tag cyan" x-text="'v' + selectedSkill?.version"></span>
                </div>
                <div class="form-label">SKILL.md Content</div>
                <div class="code-block" x-text="selectedSkill?.content"></div>
                <div style="display:flex;justify-content:flex-end;margin-top:16px;">
                    <button class="btn-cta" @click="learnSkill(selectedSkill?.skill_id)">🧠 Learn This Skill →</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Toast ═══ -->
    <div x-show="toast" x-transition class="toast" x-text="toast"></div>

    <script>
    // ═══ WebGL — Wireframe Globe with Nodes ═══
    function initGlobe() {
        const canvas = document.getElementById('webgl-canvas');
        if (!canvas || typeof THREE === 'undefined') return;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 300;

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setClearColor(0x000000, 0);

        // Globe wireframe
        const globeGeo = new THREE.SphereGeometry(80, 24, 24);
        const globeMat = new THREE.MeshBasicMaterial({ color: 0x333333, wireframe: true, transparent: true, opacity: 0.3 });
        const globe = new THREE.Mesh(globeGeo, globeMat);
        scene.add(globe);

        // Inner glow sphere
        const innerGeo = new THREE.SphereGeometry(78, 32, 32);
        const innerMat = new THREE.MeshBasicMaterial({ color: 0x00F0FF, transparent: true, opacity: 0.02 });
        scene.add(new THREE.Mesh(innerGeo, innerMat));

        // Network nodes (random points on globe surface)
        const nodeCount = 60;
        const nodePositions = [];
        for (let i = 0; i < nodeCount; i++) {
            const phi = Math.acos(-1 + (2 * i) / nodeCount);
            const theta = Math.sqrt(nodeCount * Math.PI) * phi;
            const r = 81;
            nodePositions.push(
                r * Math.cos(theta) * Math.sin(phi),
                r * Math.sin(theta) * Math.sin(phi),
                r * Math.cos(phi)
            );
        }
        const nodeGeo = new THREE.BufferGeometry();
        nodeGeo.setAttribute('position', new THREE.Float32BufferAttribute(nodePositions, 3));
        const nodeMat = new THREE.PointsMaterial({ color: 0x00F0FF, size: 2.5, transparent: true, opacity: 0.8 });
        const nodes = new THREE.Points(nodeGeo, nodeMat);
        scene.add(nodes);

        // Connection lines between nearby nodes
        const linePositions = [];
        for (let i = 0; i < nodePositions.length; i += 3) {
            for (let j = i + 3; j < nodePositions.length; j += 3) {
                const dx = nodePositions[i] - nodePositions[j];
                const dy = nodePositions[i+1] - nodePositions[j+1];
                const dz = nodePositions[i+2] - nodePositions[j+2];
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                if (dist < 100 && Math.random() > 0.5) {
                    linePositions.push(nodePositions[i], nodePositions[i+1], nodePositions[i+2]);
                    linePositions.push(nodePositions[j], nodePositions[j+1], nodePositions[j+2]);
                }
            }
        }
        const lineGeo = new THREE.BufferGeometry();
        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        const lineMat = new THREE.LineBasicMaterial({ color: 0x00F0FF, transparent: true, opacity: 0.15 });
        scene.add(new THREE.LineSegments(lineGeo, lineMat));

        // Orbit ring
        const ringGeo = new THREE.RingGeometry(100, 101, 64);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x00F0FF, transparent: true, opacity: 0.1, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = Math.PI / 2.5;
        scene.add(ring);

        // Animation
        let time = 0;
        function animate() {
            requestAnimationFrame(animate);
            time += 0.003;
            globe.rotation.y = time * 0.5;
            nodes.rotation.y = time * 0.5;
            ring.rotation.z = time * 0.2;
            nodeMat.opacity = 0.6 + Math.sin(time * 2) * 0.3;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }
    document.addEventListener('DOMContentLoaded', initGlobe);

    // ═══ Alpine.js ═══
    function marketplace() {
        return {
            view: 'home', skills: [], agents: [], stats: {},
            search: '', category: 'all',
            showPublishModal: false, selectedSkill: null,
            publishing: false, publishAgentId: '',
            toast: '', newSkill: { name: '', description: '', content: '', category: 'general' },

            async init() {
                await this.fetchStats(); await this.fetchSkills(); await this.fetchAgents();
                document.addEventListener('keydown', e => {
                    if (e.key === 'Escape') { this.showPublishModal = false; this.selectedSkill = null; }
                });
            },
            async fetchStats() { try { this.stats = await (await fetch('/api/v1/stats')).json(); } catch(e) {} },
            async fetchSkills() {
                try {
                    let url = '/api/v1/skills?status=approved';
                    if (this.category !== 'all') url += '&category=' + this.category;
                    if (this.search) url += '&search=' + encodeURIComponent(this.search);
                    this.skills = await (await fetch(url)).json();
                } catch(e) {}
            },
            async fetchAgents() { try { this.agents = await (await fetch('/api/v1/agents')).json(); } catch(e) {} },
            viewSkill(skill) { this.selectedSkill = skill; },
            async publishSkill() {
                if (!this.newSkill.name || !this.newSkill.content || !this.publishAgentId) { this.showToast('Agent ID, name, content required'); return; }
                this.publishing = true;
                try {
                    const r = await fetch('/api/v1/skills/publish?agent_id=' + this.publishAgentId, {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(this.newSkill),
                    });
                    if (r.ok) { this.showToast('Skill published ✓'); this.showPublishModal = false; this.newSkill = {name:'',description:'',content:'',category:'general'}; await this.fetchSkills(); await this.fetchStats(); }
                    else { this.showToast('Error: ' + ((await r.json()).detail || 'Unknown')); }
                } catch(e) { this.showToast('Failed'); }
                this.publishing = false;
            },
            async learnSkill(skillId) {
                if (!this.publishAgentId) { this.showToast('Set Agent ID first'); return; }
                try {
                    const r = await fetch('/api/v1/agents/' + this.publishAgentId + '/learn', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ skill_id: skillId }),
                    });
                    if (r.ok) { this.showToast('Learned 🧠'); this.selectedSkill = null; await this.fetchStats(); }
                    else { this.showToast('Error: ' + ((await r.json()).detail || 'Unknown')); }
                } catch(e) { this.showToast('Failed'); }
            },
            showToast(msg) { this.toast = msg; setTimeout(() => this.toast = '', 3000); }
        }
    }
    </script>
</body>
</html>"""


@app.get("/health")
async def health():
    # Test database connectivity
    db_status = "ok"
    try:
        from app.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"
    
    return {
        "status": "ok",
        "service": "agent-self",
        "theme": "matrix",
        "database": db_status,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
