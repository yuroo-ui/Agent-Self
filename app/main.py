"""Agent-Self - Privacy-First Skill Marketplace for AI Agents."""

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
    """Startup and shutdown events."""
    init_db()
    print("🧠 Agent-Self started!")
    print("📚 Marketplace ready at http://localhost:8000")
    yield
    print("👋 Agent-Self shutting down...")


app = FastAPI(
    title="Agent-Self",
    description="Privacy-First Skill Marketplace for AI Agents",
    version="0.1.0",
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
    """Serve the main web UI — Linear-inspired design system."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent-Self — Skill Marketplace for AI Agents</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;510;590;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        /* ═══════════════════════════════════════════════════════════
           AGENT-SELF — Linear-Inspired Design System
           Dark-mode-native marketplace for AI agent skills
           ═══════════════════════════════════════════════════════════ */

        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            /* Background Surfaces */
            --bg-canvas: #08090a;
            --bg-panel: #0f1011;
            --bg-surface: #191a1b;
            --bg-elevated: #28282c;

            /* Text */
            --text-primary: #f7f8f8;
            --text-secondary: #d0d6e0;
            --text-muted: #8a8f98;
            --text-subtle: #62666d;

            /* Brand — Indigo Violet */
            --brand: #5e6ad2;
            --accent: #7170ff;
            --accent-hover: #828fff;

            /* Status */
            --green: #10b981;
            --green-dim: rgba(16, 185, 129, 0.15);
            --yellow: #eab308;
            --yellow-dim: rgba(234, 179, 8, 0.15);
            --red: #ef4444;
            --red-dim: rgba(239, 68, 68, 0.15);
            --blue: #3b82f6;
            --blue-dim: rgba(59, 130, 246, 0.15);

            /* Borders */
            --border: rgba(255,255,255,0.08);
            --border-subtle: rgba(255,255,255,0.05);
            --border-focus: rgba(94,106,210,0.5);

            /* Shadows */
            --shadow-sm: rgba(0,0,0,0.2) 0px 1px 2px;
            --shadow-md: rgba(0,0,0,0.3) 0px 4px 12px;
            --shadow-lg: rgba(0,0,0,0.4) 0px 8px 24px;

            /* Radius */
            --radius-sm: 4px;
            --radius: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-pill: 9999px;
        }

        html {
            font-size: 16px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            font-feature-settings: 'cv01', 'ss03';
            background: var(--bg-canvas);
            color: var(--text-secondary);
            line-height: 1.5;
            min-height: 100vh;
        }

        /* ─── Typography ─── */
        h1, h2, h3, h4, h5, h6 { color: var(--text-primary); font-weight: 510; }
        a { color: var(--accent); text-decoration: none; transition: color 0.15s; }
        a:hover { color: var(--accent-hover); }

        /* ─── Layout ─── */
        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }

        /* ─── Header ─── */
        .header {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(15, 16, 17, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-subtle);
        }
        .header-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 56px;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 590;
            font-size: 15px;
            color: var(--text-primary);
            letter-spacing: -0.1px;
        }
        .logo-icon {
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, var(--brand), var(--accent));
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        .logo-badge {
            font-size: 10px;
            font-weight: 510;
            color: var(--text-muted);
            background: var(--bg-surface);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-subtle);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* ─── Nav ─── */
        .nav { display: flex; align-items: center; gap: 4px; }
        .nav-link {
            font-size: 13px;
            font-weight: 510;
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: var(--radius);
            transition: all 0.15s;
        }
        .nav-link:hover { color: var(--text-primary); background: rgba(255,255,255,0.04); }
        .nav-link.active { color: var(--text-primary); }

        /* ─── Search ─── */
        .search-box {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 0 12px;
            height: 32px;
            min-width: 240px;
            transition: all 0.15s;
        }
        .search-box:focus-within {
            border-color: var(--border-focus);
            background: rgba(255,255,255,0.05);
        }
        .search-box svg { color: var(--text-subtle); flex-shrink: 0; }
        .search-box input {
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-size: 13px;
            font-family: inherit;
            width: 100%;
        }
        .search-box input::placeholder { color: var(--text-subtle); }
        .search-kbd {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            color: var(--text-subtle);
            background: var(--bg-surface);
            padding: 2px 5px;
            border-radius: 3px;
            border: 1px solid var(--border-subtle);
        }

        /* ─── CTA Button ─── */
        .btn-primary {
            background: var(--brand);
            color: #fff;
            font-size: 13px;
            font-weight: 510;
            font-family: inherit;
            padding: 7px 14px;
            border-radius: var(--radius);
            border: none;
            cursor: pointer;
            transition: background 0.15s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .btn-primary:hover { background: var(--accent); }

        .btn-ghost {
            background: rgba(255,255,255,0.02);
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 510;
            font-family: inherit;
            padding: 7px 14px;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.15s;
        }
        .btn-ghost:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }

        /* ─── Hero ─── */
        .hero {
            padding: 80px 0 60px;
            text-align: center;
            position: relative;
        }
        .hero::before {
            content: '';
            position: absolute;
            top: -120px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 400px;
            background: radial-gradient(ellipse, rgba(94,106,210,0.12) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero h1 {
            font-size: 48px;
            font-weight: 510;
            line-height: 1.00;
            letter-spacing: -1.056px;
            margin-bottom: 16px;
            position: relative;
        }
        .hero h1 span {
            background: linear-gradient(135deg, var(--brand), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero p {
            font-size: 16px;
            color: var(--text-muted);
            max-width: 480px;
            margin: 0 auto 32px;
            line-height: 1.6;
        }

        /* ─── Stats Bar ─── */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-bottom: 0;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 590;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }
        .stat-label {
            font-size: 12px;
            color: var(--text-subtle);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 2px;
        }

        /* ─── Filter Bar ─── */
        .filter-bar {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 16px 0;
            border-bottom: 1px solid var(--border-subtle);
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .filter-chip {
            font-size: 12px;
            font-weight: 510;
            font-family: inherit;
            color: var(--text-muted);
            background: transparent;
            padding: 5px 12px;
            border-radius: var(--radius-pill);
            border: 1px solid rgba(35,37,42);
            cursor: pointer;
            transition: all 0.15s;
        }
        .filter-chip:hover { color: var(--text-secondary); border-color: var(--border); }
        .filter-chip.active {
            color: var(--text-primary);
            background: rgba(94,106,210,0.15);
            border-color: rgba(94,106,210,0.3);
        }

        /* ─── Skill Cards ─── */
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 12px;
            padding-bottom: 80px;
        }
        .skill-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .skill-card:hover {
            background: rgba(255,255,255,0.04);
            border-color: rgba(255,255,255,0.12);
            transform: translateY(-1px);
        }
        .skill-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        .skill-name {
            font-size: 15px;
            font-weight: 590;
            color: var(--text-primary);
            letter-spacing: -0.1px;
        }
        .skill-trust {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 510;
            font-family: 'JetBrains Mono', monospace;
        }
        .skill-trust.high { color: var(--green); }
        .skill-trust.medium { color: var(--yellow); }
        .skill-trust.low { color: var(--red); }

        .skill-desc {
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .skill-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .skill-tag {
            font-size: 11px;
            font-weight: 510;
            color: var(--text-muted);
            background: var(--bg-surface);
            padding: 3px 8px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-subtle);
        }
        .skill-tag.version {
            color: var(--accent);
            background: rgba(113,112,255,0.1);
            border-color: rgba(113,112,255,0.2);
        }
        .skill-tag.downloads {
            color: var(--text-subtle);
            background: transparent;
            border: none;
            padding: 3px 0;
        }

        /* ─── Security Badge ─── */
        .security-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 510;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
        }
        .security-badge.clean {
            color: var(--green);
            background: var(--green-dim);
        }
        .security-badge.suspicious {
            color: var(--yellow);
            background: var(--yellow-dim);
        }
        .security-badge.malicious {
            color: var(--red);
            background: var(--red-dim);
        }
        .security-badge.scanning {
            color: var(--blue);
            background: var(--blue-dim);
        }

        /* ─── Modal ─── */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.75);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 200;
            padding: 24px;
            backdrop-filter: blur(4px);
        }
        .modal {
            background: var(--bg-panel);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            width: 100%;
            max-width: 640px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 24px 24px 20px;
            border-bottom: 1px solid var(--border-subtle);
        }
        .modal-title {
            font-size: 18px;
            font-weight: 590;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }
        .modal-subtitle {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        .modal-close {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: var(--radius);
            border: none;
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 18px;
            transition: all 0.15s;
        }
        .modal-close:hover { background: rgba(255,255,255,0.05); color: var(--text-primary); }
        .modal-body { padding: 24px; }

        /* ─── Form Inputs ─── */
        .form-group { margin-bottom: 20px; }
        .form-label {
            display: block;
            font-size: 13px;
            font-weight: 510;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }
        .form-input, .form-select, .form-textarea {
            width: 100%;
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 10px 12px;
            color: var(--text-primary);
            font-size: 14px;
            font-family: inherit;
            transition: all 0.15s;
        }
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--border-focus);
            background: rgba(255,255,255,0.04);
        }
        .form-textarea {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
            resize: vertical;
            min-height: 200px;
        }
        .form-select {
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2362666d' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            padding-right: 32px;
        }
        .form-select option { background: var(--bg-surface); }
        .form-hint {
            font-size: 12px;
            color: var(--text-subtle);
            margin-top: 6px;
        }

        /* ─── Code Preview ─── */
        .code-block {
            background: var(--bg-canvas);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius);
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
            color: var(--text-secondary);
            overflow-x: auto;
            white-space: pre-wrap;
            margin-top: 16px;
        }

        /* ─── Trust Score Bar ─── */
        .trust-bar {
            display: flex;
            gap: 12px;
            margin: 20px 0;
        }
        .trust-stat {
            flex: 1;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 16px;
            text-align: center;
        }
        .trust-stat-value {
            font-size: 28px;
            font-weight: 590;
            letter-spacing: -1px;
        }
        .trust-stat-label {
            font-size: 11px;
            color: var(--text-subtle);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }

        /* ─── Empty State ─── */
        .empty-state {
            text-align: center;
            padding: 80px 24px;
            color: var(--text-subtle);
        }
        .empty-state-icon {
            font-size: 40px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        /* ─── Toast ─── */
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--bg-surface);
            border: 1px solid var(--green);
            color: var(--green);
            padding: 12px 20px;
            border-radius: var(--radius);
            font-size: 13px;
            font-weight: 510;
            box-shadow: var(--shadow-md);
            z-index: 300;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* ─── Skeleton Loading ─── */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .skeleton {
            background: linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-elevated) 50%, var(--bg-surface) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: var(--radius-sm);
        }

        /* ─── Responsive ─── */
        @media (max-width: 768px) {
            .hero h1 { font-size: 32px; letter-spacing: -0.7px; }
            .stats-bar { gap: 20px; }
            .stat-value { font-size: 20px; }
            .skills-grid { grid-template-columns: 1fr; }
            .search-box { min-width: 180px; }
            .nav { display: none; }
        }
        @media (max-width: 480px) {
            .hero { padding: 48px 0 40px; }
            .hero h1 { font-size: 28px; }
            .container { padding: 0 16px; }
        }

        /* ─── Scrollbar ─── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

        /* ─── Pulse animation for scanning ─── */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
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
                <a href="#" class="nav-link active">Explore</a>
                <a href="#" class="nav-link">Trending</a>
                <a href="#" class="nav-link">Categories</a>
                <a href="#" class="nav-link">Docs</a>
            </nav>

            <div style="display:flex;align-items:center;gap:12px;">
                <div class="search-box">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" placeholder="Search skills..." x-model="search" @input.debounce.300ms="fetchSkills()">
                    <span class="search-kbd">/</span>
                </div>
                <button class="btn-primary" @click="showSubmitModal = true">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
                    Submit
                </button>
            </div>
        </div>
    </header>

    <!-- ═══ Hero ═══ -->
    <section class="hero">
        <div class="container">
            <h1>Skills for <span>AI Agents</span></h1>
            <p>Verified. Secure. Privacy-preserving. A marketplace where agents learn from each other without compromising safety.</p>
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value" x-text="stats.total_skills || '—'">—</div>
                    <div class="stat-label">Skills</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" x-text="stats.approved_skills || '—'">—</div>
                    <div class="stat-label">Verified</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" x-text="stats.total_users || '—'">—</div>
                    <div class="stat-label">Agents</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" x-text="(stats.avg_trust_score || 0).toFixed(0) + '%'">—</div>
                    <div class="stat-label">Avg Trust</div>
                </div>
            </div>
        </div>
    </section>

    <!-- ═══ Main Content ═══ -->
    <main class="container" style="padding-top:16px;">

        <!-- Filter Bar -->
        <div class="filter-bar">
            <button class="filter-chip" :class="category === 'all' ? 'active' : ''" @click="category='all'; fetchSkills()">All</button>
            <template x-for="cat in (stats.categories || [])" :key="cat">
                <button class="filter-chip" :class="category === cat ? 'active' : ''" @click="category=cat; fetchSkills()" x-text="cat"></button>
            </template>
        </div>

        <!-- Skills Grid -->
        <div class="skills-grid">
            <template x-for="skill in skills" :key="skill.id">
                <div class="skill-card" @click="viewSkill(skill.slug)">
                    <div class="skill-card-header">
                        <div class="skill-name" x-text="skill.name"></div>
                        <div class="skill-trust" :class="skill.trust_score >= 80 ? 'high' : skill.trust_score >= 50 ? 'medium' : 'low'">
                            <span x-text="skill.trust_score.toFixed(0)"></span>
                            <span style="color:var(--text-subtle);font-weight:400;">trust</span>
                        </div>
                    </div>
                    <div class="skill-desc" x-text="skill.description"></div>
                    <div class="skill-meta">
                        <span class="security-badge" :class="skill.scan_result || 'scanning'">
                            <span x-text="skill.scan_result === 'clean' ? '✓' : skill.scan_result === 'suspicious' ? '⚠' : skill.scan_result === 'malicious' ? '✗' : '◌'"></span>
                            <span x-text="skill.scan_result || 'scanning'"></span>
                        </span>
                        <span class="skill-tag" x-text="skill.category"></span>
                        <span class="skill-tag version" x-text="'v' + skill.version"></span>
                        <span class="skill-tag downloads" x-text="skill.download_count + ' ↓'"></span>
                    </div>
                </div>
            </template>
        </div>

        <!-- Empty State -->
        <div x-show="skills.length === 0 && !loading" class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <p>No skills found</p>
        </div>
    </main>

    <!-- ═══ Submit Modal ═══ -->
    <div x-show="showSubmitModal" x-transition.opacity class="modal-overlay" @click.self="showSubmitModal = false">
        <div class="modal">
            <div class="modal-header">
                <div>
                    <div class="modal-title">Submit Skill</div>
                    <div class="modal-subtitle">Your skill will be security-scanned before publishing</div>
                </div>
                <button class="modal-close" @click="showSubmitModal = false">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Skill Name</label>
                    <input type="text" class="form-input" x-model="newSkill.name" placeholder="e.g. web-scraper-v2">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" x-model="newSkill.description" placeholder="What does this skill do?">
                </div>
                <div class="form-group">
                    <label class="form-label">Code</label>
                    <textarea class="form-textarea" x-model="newSkill.code" placeholder="# Your skill code here..."></textarea>
                    <div class="form-hint">Code will be scanned for malware, network access, and dangerous patterns</div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select class="form-select" x-model="newSkill.category">
                            <template x-for="cat in (stats.categories || ['general'])" :key="cat">
                                <option :value="cat" x-text="cat"></option>
                            </template>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">License</label>
                        <select class="form-select" x-model="newSkill.license">
                            <option value="MIT">MIT</option>
                            <option value="Apache-2.0">Apache 2.0</option>
                            <option value="GPL-3.0">GPL 3.0</option>
                        </select>
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:8px;">
                    <button class="btn-ghost" @click="showSubmitModal = false">Cancel</button>
                    <button class="btn-primary" @click="submitSkill()" :disabled="submitting">
                        <span x-show="!submitting">Submit & Scan</span>
                        <span x-show="submitting" class="pulse">Scanning...</span>
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
                    <div class="modal-subtitle">by <span x-text="selectedSkill?.author?.username || 'anonymous'"></span></div>
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
                        <div class="trust-stat-value" :style="'color:' + (selectedSkill?.scan_result === 'clean' ? 'var(--green)' : 'var(--yellow)')" x-text="(selectedSkill?.scan_result || 'SCANNING').toUpperCase()"></div>
                        <div class="trust-stat-label">Security</div>
                    </div>
                    <div class="trust-stat">
                        <div class="trust-stat-value" style="color:var(--text-primary);" x-text="selectedSkill?.download_count || 0"></div>
                        <div class="trust-stat-label">Downloads</div>
                    </div>
                </div>

                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;">
                    <span class="skill-tag" x-text="selectedSkill?.category"></span>
                    <span class="skill-tag version" x-text="'v' + selectedSkill?.version"></span>
                    <template x-for="tag in selectedSkill?.tags || []" :key="tag">
                        <span class="skill-tag" x-text="tag"></span>
                    </template>
                </div>

                <div class="form-label" style="margin-top:20px;">Code</div>
                <div class="code-block" x-text="selectedSkill?.code"></div>
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
            skills: [],
            stats: {},
            search: '',
            category: 'all',
            showSubmitModal: false,
            selectedSkill: null,
            submitting: false,
            loading: true,
            toast: '',
            newSkill: { name: '', description: '', code: '', category: 'general', license: 'MIT' },

            async init() {
                await this.fetchStats();
                await this.fetchSkills();
                this.loading = false;

                // Keyboard shortcut: / to focus search
                document.addEventListener('keydown', (e) => {
                    if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                        e.preventDefault();
                        document.querySelector('.search-box input')?.focus();
                    }
                    if (e.key === 'Escape') {
                        this.showSubmitModal = false;
                        this.selectedSkill = null;
                    }
                });
            },

            async fetchStats() {
                try {
                    const res = await fetch('/api/v1/stats');
                    this.stats = await res.json();
                } catch (e) { console.error('Stats fetch failed:', e); }
            },

            async fetchSkills() {
                try {
                    let url = '/api/v1/skills?status=approved';
                    if (this.category !== 'all') url += '&category=' + this.category;
                    if (this.search) url += '&search=' + encodeURIComponent(this.search);
                    const res = await fetch(url);
                    this.skills = await res.json();
                } catch (e) { console.error('Skills fetch failed:', e); }
            },

            async viewSkill(slug) {
                try {
                    const res = await fetch('/api/v1/skills/' + slug);
                    this.selectedSkill = await res.json();
                } catch (e) { console.error('Skill fetch failed:', e); }
            },

            async submitSkill() {
                if (!this.newSkill.name || !this.newSkill.code) {
                    this.showToast('Name and code are required');
                    return;
                }
                this.submitting = true;
                try {
                    const res = await fetch('/api/v1/skills', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.newSkill),
                    });
                    if (res.ok) {
                        this.showToast('Skill submitted & scanned ✓');
                        this.showSubmitModal = false;
                        this.newSkill = { name: '', description: '', code: '', category: 'general', license: 'MIT' };
                        await this.fetchSkills();
                        await this.fetchStats();
                    } else {
                        const err = await res.json();
                        this.showToast('Error: ' + (err.detail || 'Unknown'));
                    }
                } catch (e) { this.showToast('Submit failed'); }
                this.submitting = false;
            },

            showToast(msg) {
                this.toast = msg;
                setTimeout(() => this.toast = '', 3000);
            }
        }
    }
    </script>
</body>
</html>"""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agent-self"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
