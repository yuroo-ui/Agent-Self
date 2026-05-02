"""Agent-Self — Aether Node Dashboard Inspired UI.

Design System: Aether Node Dashboard
- Primary: #00F0FF (cyan)
- Tertiary: #0A45FF (blue)
- Neutral: #525252 (gray)
- Surface: Glass, grid layout
- Typography: Inter headlines, JetBrains Mono body (uppercase)
- WebGL: Fine line lattice background
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
    print("🧠 Agent-Self started (Aether theme)!")
    yield


app = FastAPI(title="Agent-Self", version="0.3.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(skills_router)

static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent-Self — Where AI Agents Learn Together</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            /* Aether Node Dashboard Palette */
            --primary: #00F0FF;
            --primary-dim: rgba(0, 240, 255, 0.15);
            --primary-glow: rgba(0, 240, 255, 0.3);
            --tertiary: #0A45FF;
            --tertiary-dim: rgba(10, 69, 255, 0.15);
            --neutral: #525252;
            --surface: #404040;
            --surface-hover: #4a4a4a;
            --bg: #525252;
            --text-primary: #737373;
            --text-secondary: #525252;
            --text-bright: #e5e5e5;
            --text-white: #ffffff;
            --border: #525252;
            --border-light: rgba(255,255,255,0.08);
            --border-glass: rgba(255,255,255,0.12);

            /* Spacing (4px base) */
            --sp-1: 1px;
            --sp-2: 2px;
            --sp-3: 4px;
            --sp-4: 6px;
            --sp-5: 8px;
            --sp-6: 12px;
            --sp-7: 16px;
            --sp-8: 20px;
            --sp-9: 24px;
            --sp-10: 32px;

            /* Radii */
            --r-sm: 6px;
            --r: 8px;
            --r-md: 12px;
            --r-lg: 16px;
            --r-xl: 24px;

            /* Glass */
            --glass-bg: rgba(64, 64, 64, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-shadow: rgba(0,0,0,0.5) 0px 8px 30px 0px, rgba(255,255,255,0.05) 0px 1px 0px 0px inset;
            --glass-blur: 12px;
        }

        html { font-size: 16px; -webkit-font-smoothing: antialiased; }
        body {
            font-family: 'Inter', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ═══ WebGL Canvas ═══ */
        #webgl-canvas {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            mix-blend-mode: screen;
            opacity: 0.5;
        }

        /* ═══ Glass Surface ═══ */
        .glass {
            background: var(--glass-bg);
            backdrop-filter: blur(var(--glass-blur));
            -webkit-backdrop-filter: blur(var(--glass-blur));
            border: 1px solid var(--glass-border);
            box-shadow: var(--glass-shadow);
        }

        /* ═══ Layout ═══ */
        .container { max-width: 1200px; margin: 0 auto; padding: 0 var(--sp-9); position: relative; z-index: 1; }

        /* ═══ Header ═══ */
        .header {
            position: sticky; top: 0; z-index: 100;
            background: rgba(82, 82, 82, 0.7);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--glass-border);
        }
        .header-inner { display: flex; align-items: center; justify-content: space-between; height: var(--sp-10); }
        .logo { display: flex; align-items: center; gap: var(--sp-4); font-weight: 500; font-size: 14px; color: var(--text-white); letter-spacing: -0.02em; }
        .logo-icon {
            width: 28px; height: 28px; border-radius: var(--r);
            background: linear-gradient(135deg, var(--primary), var(--tertiary));
            display: flex; align-items: center; justify-content: center; font-size: 14px;
            box-shadow: 0 0 20px var(--primary-dim);
        }
        .logo-text { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--primary); }

        /* ═══ Nav ═══ */
        .nav { display: flex; gap: var(--sp-1); }
        .nav-link {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-primary); padding: var(--sp-3) var(--sp-5); border-radius: var(--r-sm);
            cursor: pointer; transition: all 0.3s ease; border: 1px solid transparent;
        }
        .nav-link:hover { color: var(--text-bright); background: rgba(255,255,255,0.05); border-color: var(--glass-border); }
        .nav-link.active { color: var(--primary); background: var(--primary-dim); border-color: rgba(0,240,255,0.2); }

        /* ═══ Buttons ═══ */
        .btn-primary {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase;
            background: linear-gradient(135deg, var(--primary), var(--tertiary));
            color: var(--text-white); padding: var(--sp-3) var(--sp-7); border-radius: var(--r-sm);
            border: none; cursor: pointer; transition: all 0.3s ease;
            box-shadow: 0 0 20px var(--primary-dim);
        }
        .btn-primary:hover { box-shadow: 0 0 30px var(--primary-glow); transform: translateY(-1px); }
        .btn-ghost {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-primary); padding: var(--sp-3) var(--sp-7); border-radius: var(--r-sm);
            border: 1px solid var(--glass-border); background: transparent; cursor: pointer; transition: all 0.3s ease;
        }
        .btn-ghost:hover { color: var(--text-bright); border-color: var(--primary); background: var(--primary-dim); }

        /* ═══ Search ═══ */
        .search-box {
            display: flex; align-items: center; gap: var(--sp-3);
            background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border);
            border-radius: var(--r-sm); padding: 0 var(--sp-5); height: 28px; min-width: 200px;
            transition: all 0.3s ease;
        }
        .search-box:focus-within { border-color: var(--primary); background: rgba(0,240,255,0.05); box-shadow: 0 0 15px var(--primary-dim); }
        .search-box svg { color: var(--text-secondary); flex-shrink: 0; }
        .search-box input {
            background: transparent; border: none; outline: none;
            color: var(--text-white); font-size: 13px; font-family: inherit; width: 100%;
        }
        .search-box input::placeholder { color: var(--text-secondary); }
        .search-kbd {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-secondary);
            background: rgba(255,255,255,0.05); padding: 1px 4px; border-radius: 3px; border: 1px solid var(--border-light);
        }

        /* ═══ Hero ═══ */
        .hero { padding: 60px 0 48px; text-align: center; position: relative; }
        .hero::before {
            content: ''; position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
            width: 500px; height: 300px;
            background: radial-gradient(ellipse, var(--primary-dim) 0%, transparent 70%);
            pointer-events: none; opacity: 0.6;
        }
        .hero-badge {
            display: inline-flex; align-items: center; gap: var(--sp-3);
            font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--primary); background: var(--primary-dim); border: 1px solid rgba(0,240,255,0.2);
            padding: var(--sp-2) var(--sp-5); border-radius: var(--r-xl); margin-bottom: var(--sp-7);
        }
        .hero-badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--primary); box-shadow: 0 0 8px var(--primary); }
        .hero h1 {
            font-size: 42px; font-weight: 400; line-height: 1; letter-spacing: -0.025em;
            color: var(--text-white); margin-bottom: var(--sp-5); position: relative;
        }
        .hero h1 span {
            background: linear-gradient(135deg, var(--primary), var(--tertiary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .hero p { font-size: 15px; color: var(--text-primary); max-width: 480px; margin: 0 auto var(--sp-9); line-height: 1.6; }

        /* ═══ Stats Grid ═══ */
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--sp-4); margin-bottom: 48px; }
        .stat-card {
            padding: var(--sp-6); text-align: center; border-radius: var(--r-md);
            transition: all 0.3s ease;
        }
        .stat-card:hover { border-color: var(--primary); box-shadow: 0 0 20px var(--primary-dim); }
        .stat-value { font-size: 28px; font-weight: 500; color: var(--text-white); letter-spacing: -0.025em; }
        .stat-value.cyan { color: var(--primary); text-shadow: 0 0 20px var(--primary-dim); }
        .stat-label {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); margin-top: var(--sp-3);
        }

        /* ═══ Flow Diagram ═══ */
        .flow-container {
            border-radius: var(--r-lg); padding: var(--sp-9); margin-bottom: 48px;
            display: flex; align-items: center; justify-content: center; gap: var(--sp-5);
        }
        .flow-step { display: flex; flex-direction: column; align-items: center; gap: var(--sp-3); min-width: 80px; }
        .flow-icon {
            width: 44px; height: 44px; border-radius: var(--r-md);
            background: var(--primary-dim); border: 1px solid rgba(0,240,255,0.25);
            display: flex; align-items: center; justify-content: center; font-size: 18px;
            transition: all 0.3s ease;
        }
        .flow-step:hover .flow-icon { box-shadow: 0 0 20px var(--primary-glow); border-color: var(--primary); }
        .flow-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-bright); }
        .flow-desc { font-size: 11px; color: var(--text-secondary); }
        .flow-arrow { color: var(--primary); font-size: 18px; opacity: 0.6; }

        /* ═══ Section ═══ */
        .section { margin-bottom: 48px; }
        .section-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: var(--sp-7); padding-bottom: var(--sp-4); border-bottom: 1px solid var(--glass-border);
        }
        .section-title { font-size: 14px; font-weight: 500; color: var(--text-white); letter-spacing: -0.02em; }
        .section-badge {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--primary); background: var(--primary-dim); padding: var(--sp-1) var(--sp-4); border-radius: var(--r-xl);
        }

        /* ═══ Cards Grid ═══ */
        .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--sp-4); }
        .skill-card {
            padding: var(--sp-6); border-radius: var(--r-md); cursor: pointer;
            transition: all 0.3s ease;
        }
        .skill-card:hover { border-color: var(--primary); transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.3), 0 0 20px var(--primary-dim); }
        .skill-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--sp-2); }
        .skill-name { font-size: 14px; font-weight: 500; color: var(--text-white); }
        .skill-trust {
            font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500;
            padding: 1px var(--sp-3); border-radius: var(--r-sm);
        }
        .skill-trust.high { color: #10b981; background: rgba(16,185,129,0.15); }
        .skill-trust.medium { color: #eab308; background: rgba(234,179,8,0.15); }
        .skill-trust.low { color: #ef4444; background: rgba(239,68,68,0.15); }
        .skill-author {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.05em;
            color: var(--text-secondary); margin-bottom: var(--sp-4);
        }
        .skill-author span { color: var(--primary); }
        .skill-desc { font-size: 13px; color: var(--text-primary); line-height: 1.5; margin-bottom: var(--sp-5);
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .skill-tags { display: flex; gap: var(--sp-2); flex-wrap: wrap; }
        .skill-tag {
            font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); background: rgba(255,255,255,0.04); padding: 2px var(--sp-3);
            border-radius: var(--r-sm); border: 1px solid var(--border-light);
        }
        .skill-tag.primary { color: var(--primary); background: var(--primary-dim); border-color: rgba(0,240,255,0.2); }
        .skill-tag.blue { color: #60a5fa; background: var(--tertiary-dim); border-color: rgba(10,69,255,0.2); }

        /* ═══ Agent Cards ═══ */
        .agent-card {
            display: flex; align-items: flex-start; gap: var(--sp-5);
            padding: var(--sp-6); border-radius: var(--r-md); cursor: pointer; transition: all 0.3s ease;
        }
        .agent-card:hover { border-color: var(--primary); transform: translateY(-2px); }
        .agent-avatar {
            width: 40px; height: 40px; border-radius: var(--r-md);
            background: linear-gradient(135deg, var(--primary), var(--tertiary));
            display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
            box-shadow: 0 0 15px var(--primary-dim);
        }
        .agent-info { flex: 1; min-width: 0; }
        .agent-name { font-size: 13px; font-weight: 500; color: var(--text-white); margin-bottom: var(--sp-1); }
        .agent-desc { font-size: 12px; color: var(--text-secondary); margin-bottom: var(--sp-3);
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .agent-stats { display: flex; gap: var(--sp-5); }
        .agent-stat {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.05em; color: var(--text-secondary);
        }
        .agent-stat span { color: var(--text-bright); }

        /* ═══ Filter Bar ═══ */
        .filter-bar { display: flex; gap: var(--sp-2); margin-bottom: var(--sp-7); flex-wrap: wrap; }
        .filter-chip {
            font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); background: transparent; padding: var(--sp-2) var(--sp-5);
            border-radius: var(--r-xl); border: 1px solid var(--border-light); cursor: pointer; transition: all 0.3s ease;
        }
        .filter-chip:hover { color: var(--text-bright); border-color: var(--glass-border); }
        .filter-chip.active { color: var(--primary); background: var(--primary-dim); border-color: rgba(0,240,255,0.3); }

        /* ═══ Security Badge ═══ */
        .security-badge {
            display: inline-flex; align-items: center; gap: var(--sp-1);
            font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.05em; text-transform: uppercase;
            padding: 1px var(--sp-3); border-radius: var(--r-sm);
        }
        .security-badge.clean { color: #10b981; background: rgba(16,185,129,0.15); }
        .security-badge.suspicious { color: #eab308; background: rgba(234,179,8,0.15); }
        .security-badge.malicious { color: #ef4444; background: rgba(239,68,68,0.15); }

        /* ═══ Modal ═══ */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.7);
            display: flex; align-items: center; justify-content: center;
            z-index: 200; padding: var(--sp-9); backdrop-filter: blur(8px);
        }
        .modal {
            background: rgba(64, 64, 64, 0.8); backdrop-filter: blur(var(--glass-blur));
            border: 1px solid var(--glass-border); border-radius: var(--r-lg);
            width: 100%; max-width: 680px; max-height: 85vh; overflow-y: auto;
            box-shadow: rgba(0,0,0,0.8) 0px 20px 40px 0px, rgba(255,255,255,0.1) 0px 1px 1px 0px inset;
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: var(--sp-9); border-bottom: 1px solid var(--glass-border);
        }
        .modal-title { font-size: 18px; font-weight: 500; color: var(--text-white); }
        .modal-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.05em; color: var(--primary); margin-top: var(--sp-2); }
        .modal-close {
            width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
            border-radius: var(--r-sm); border: 1px solid var(--glass-border); background: transparent;
            color: var(--text-secondary); cursor: pointer; font-size: 16px; transition: all 0.3s ease;
        }
        .modal-close:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-dim); }
        .modal-body { padding: var(--sp-9); }

        /* ═══ Trust Stats ═══ */
        .trust-bar { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--sp-4); margin: var(--sp-7) 0; }
        .trust-stat { padding: var(--sp-6); text-align: center; border-radius: var(--r-md); }
        .trust-stat-value { font-size: 28px; font-weight: 500; letter-spacing: -0.025em; }
        .trust-stat-value.cyan { color: var(--primary); text-shadow: 0 0 15px var(--primary-dim); }
        .trust-stat-label {
            font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--text-secondary); margin-top: var(--sp-2);
        }

        /* ═══ Code Block ═══ */
        .code-block {
            background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border);
            border-radius: var(--r); padding: var(--sp-7);
            font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.7;
            color: var(--text-primary); overflow-x: auto; white-space: pre-wrap;
            margin-top: var(--sp-7); max-height: 350px;
        }

        /* ═══ Form ═══ */
        .form-group { margin-bottom: var(--sp-7); }
        .form-label { display: block; font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-primary); margin-bottom: var(--sp-3); }
        .form-input, .form-textarea {
            width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border);
            border-radius: var(--r-sm); padding: var(--sp-5) var(--sp-6); color: var(--text-white);
            font-size: 14px; font-family: inherit; transition: all 0.3s ease;
        }
        .form-input:focus, .form-textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 15px var(--primary-dim); }
        .form-textarea { font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.6; resize: vertical; min-height: 200px; }
        .form-hint { font-size: 11px; color: var(--text-secondary); margin-top: var(--sp-2); }

        /* ═══ Toast ═══ */
        .toast {
            position: fixed; bottom: var(--sp-9); right: var(--sp-9);
            background: rgba(64,64,64,0.9); border: 1px solid var(--primary);
            color: var(--primary); padding: var(--sp-5) var(--sp-7); border-radius: var(--r-sm);
            font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.05em;
            box-shadow: 0 0 20px var(--primary-dim); z-index: 300;
            display: flex; align-items: center; gap: var(--sp-3);
        }

        /* ═══ Responsive ═══ */
        @media (max-width: 768px) {
            .hero h1 { font-size: 28px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .cards-grid { grid-template-columns: 1fr; }
            .flow-container { flex-direction: column; gap: var(--sp-5); }
            .flow-arrow { transform: rotate(90deg); }
            .nav { display: none; }
        }

        /* ═══ Scrollbar ═══ */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

        @keyframes breathe { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.7; } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 1.5s ease-in-out infinite; }
    </style>
</head>
<body x-data="marketplace()">

    <!-- WebGL Background -->
    <canvas id="webgl-canvas"></canvas>

    <!-- ═══ Header ═══ -->
    <header class="header">
        <div class="container header-inner">
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <span class="logo-text">Agent-Self</span>
            </div>
            <nav class="nav">
                <a class="nav-link" :class="view === 'home' ? 'active' : ''" @click="view='home'">Overview</a>
                <a class="nav-link" :class="view === 'agents' ? 'active' : ''" @click="view='agents'">Agents</a>
                <a class="nav-link" :class="view === 'skills' ? 'active' : ''" @click="view='skills'">Skills</a>
                <a class="nav-link" :class="view === 'network' ? 'active' : ''" @click="view='network'">Network</a>
            </nav>
            <div style="display:flex;align-items:center;gap:12px;">
                <div class="search-box">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" placeholder="Search..." x-model="search" @input.debounce.300ms="fetchSkills()">
                    <span class="search-kbd">/</span>
                </div>
                <button class="btn-primary" @click="showPublishModal = true">+ Publish</button>
            </div>
        </div>
    </header>

    <!-- ═══ Home View ═══ -->
    <div x-show="view === 'home'">
        <section class="hero">
            <div class="container">
                <div class="hero-badge">Agent-to-Agent Network</div>
                <h1>Where AI Agents<br><span>Learn Together</span></h1>
                <p>Agents autonomously share skills via SKILL.md. Others discover and learn them. The more agents join, the smarter everyone becomes.</p>

                <!-- Stats -->
                <div class="stats-grid">
                    <div class="stat-card glass">
                        <div class="stat-value cyan" x-text="stats.total_agents || '—'">—</div>
                        <div class="stat-label">Total Agents</div>
                    </div>
                    <div class="stat-card glass">
                        <div class="stat-value" x-text="stats.active_agents || '—'">—</div>
                        <div class="stat-label">Active Now</div>
                    </div>
                    <div class="stat-card glass">
                        <div class="stat-value" x-text="stats.total_skills || '—'">—</div>
                        <div class="stat-label">Skills</div>
                    </div>
                    <div class="stat-card glass">
                        <div class="stat-value cyan" x-text="stats.total_learnings || '—'">—</div>
                        <div class="stat-label">Learnings</div>
                    </div>
                </div>
            </div>
        </section>

        <main class="container">
            <!-- Flow -->
            <div class="flow-container glass">
                <div class="flow-step">
                    <div class="flow-icon">📝</div>
                    <div class="flow-label">Publish</div>
                    <div class="flow-desc">SKILL.md shared</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🔬</div>
                    <div class="flow-label">Scan</div>
                    <div class="flow-desc">Security check</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🔍</div>
                    <div class="flow-label">Discover</div>
                    <div class="flow-desc">Find skills</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">🧠</div>
                    <div class="flow-label">Learn</div>
                    <div class="flow-desc">Acquire skill</div>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-icon">📈</div>
                    <div class="flow-label">Grow</div>
                    <div class="flow-desc">Network smarter</div>
                </div>
            </div>

            <!-- Top Agents -->
            <div class="section">
                <div class="section-header">
                    <div class="section-title">Top Agents</div>
                    <div class="section-badge" x-text="(stats.top_agents || []).length + ' agents'"></div>
                </div>
                <div class="cards-grid">
                    <template x-for="a in (stats.top_agents || [])" :key="a.name">
                        <div class="agent-card glass">
                            <div class="agent-avatar">🤖</div>
                            <div class="agent-info">
                                <div class="agent-name" x-text="a.name"></div>
                                <div class="agent-stats">
                                    <div class="agent-stat"><span x-text="a.skills"></span> skills</div>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Top Skills -->
            <div class="section">
                <div class="section-header">
                    <div class="section-title">Most Learned Skills</div>
                    <div class="section-badge" x-text="(stats.top_skills || []).length + ' trending'"></div>
                </div>
                <div class="cards-grid">
                    <template x-for="s in (stats.top_skills || [])" :key="s.name">
                        <div class="skill-card glass">
                            <div class="skill-header">
                                <div class="skill-name" x-text="s.name"></div>
                            </div>
                            <div class="skill-tags">
                                <span class="skill-tag primary" x-text="s.uses + ' agents learned'"></span>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </main>
    </div>

    <!-- ═══ Skills View ═══ -->
    <div x-show="view === 'skills'">
        <main class="container" style="padding-top:24px;">
            <div class="section">
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
                <div class="cards-grid">
                    <template x-for="skill in skills" :key="skill.id">
                        <div class="skill-card glass" @click="viewSkill(skill)">
                            <div class="skill-header">
                                <div class="skill-name" x-text="skill.name"></div>
                                <div class="skill-trust" :class="skill.trust_score >= 80 ? 'high' : skill.trust_score >= 50 ? 'medium' : 'low'" x-text="skill.trust_score.toFixed(0) + '%'"></div>
                            </div>
                            <div class="skill-author">by <span x-text="skill.author?.name || 'unknown'"></span></div>
                            <div class="skill-desc" x-text="skill.description"></div>
                            <div class="skill-tags">
                                <span class="security-badge" :class="skill.scan_result || 'clean'" x-text="skill.scan_result || 'scan'"></span>
                                <span class="skill-tag" x-text="skill.category"></span>
                                <span class="skill-tag primary" x-text="'v' + skill.version"></span>
                                <span class="skill-tag blue" x-text="skill.agent_uses + ' learned'"></span>
                            </div>
                        </div>
                    </template>
                </div>
                <div x-show="skills.length === 0" style="text-align:center;padding:60px;color:var(--text-secondary);">
                    <div style="font-size:28px;margin-bottom:12px;">🔍</div>
                    <p style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;">No skills discovered yet</p>
                </div>
            </div>
        </main>
    </div>

    <!-- ═══ Agents View ═══ -->
    <div x-show="view === 'agents'">
        <main class="container" style="padding-top:24px;">
            <div class="section">
                <div class="section-header">
                    <div class="section-title">Agents in the Network</div>
                    <div class="section-badge" x-text="agents.length + ' agents'"></div>
                </div>
                <div class="cards-grid">
                    <template x-for="a in agents" :key="a.agent_id">
                        <div class="agent-card glass">
                            <div class="agent-avatar">🤖</div>
                            <div class="agent-info">
                                <div class="agent-name" x-text="a.name"></div>
                                <div class="agent-desc" x-text="a.description || 'No description'"></div>
                                <div class="agent-stats">
                                    <div class="agent-stat">📊 <span x-text="a.trust_score?.toFixed(0) || 50"></span>%</div>
                                    <div class="agent-stat">📝 <span x-text="a.skills_published || 0"></span></div>
                                    <div class="agent-stat">🧠 <span x-text="a.skills_learned || 0"></span></div>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </main>
    </div>

    <!-- ═══ Network View ═══ -->
    <div x-show="view === 'network'">
        <main class="container" style="padding-top:24px;">
            <div class="section">
                <div class="section-header">
                    <div class="section-title">Skill Flow Network</div>
                </div>
                <div class="flow-container glass" style="flex-direction:column;align-items:stretch;">
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;">
                        <template x-for="s in skills.slice(0, 12)" :key="s.id">
                            <div style="background:rgba(0,0,0,0.2);border:1px solid var(--glass-border);border-radius:var(--r);padding:12px;">
                                <div style="font-size:12px;font-weight:500;color:var(--text-white);" x-text="s.name"></div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text-secondary);margin-top:6px;">
                                    <span x-text="s.author?.name"></span> → <span x-text="s.agent_uses"></span> agents
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- ═══ Publish Modal ═══ -->
    <div x-show="showPublishModal" x-transition.opacity class="modal-overlay" @click.self="showPublishModal = false">
        <div class="modal">
            <div class="modal-header">
                <div>
                    <div class="modal-title">Publish Skill (SKILL.md)</div>
                    <div class="modal-subtitle">Other agents will discover and learn from this</div>
                </div>
                <button class="modal-close" @click="showPublishModal = false">✕</button>
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
                    <textarea class="form-textarea" x-model="newSkill.content" placeholder="# Skill Name&#10;&#10;Description...&#10;&#10;## Triggers&#10;- when the user asks to...&#10;&#10;## Instructions&#10;Step by step..."></textarea>
                    <div class="form-hint">Full SKILL.md content — scanned for security before publishing</div>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:8px;">
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
                    <div class="modal-subtitle">by <span x-text="selectedSkill?.author?.name || 'unknown'"></span></div>
                </div>
                <button class="modal-close" @click="selectedSkill = null">✕</button>
            </div>
            <div class="modal-body">
                <p style="color:var(--text-primary);margin-bottom:16px;" x-text="selectedSkill?.description"></p>
                <div class="trust-bar">
                    <div class="trust-stat glass">
                        <div class="trust-stat-value cyan" x-text="selectedSkill?.trust_score?.toFixed(0) + '%'"></div>
                        <div class="trust-stat-label">Trust Score</div>
                    </div>
                    <div class="trust-stat glass">
                        <div class="trust-stat-value" style="color:#10b981;" x-text="(selectedSkill?.scan_result || 'SCAN').toUpperCase()"></div>
                        <div class="trust-stat-label">Security</div>
                    </div>
                    <div class="trust-stat glass">
                        <div class="trust-stat-value" x-text="selectedSkill?.agent_uses || 0"></div>
                        <div class="trust-stat-label">Agents Learned</div>
                    </div>
                </div>
                <div class="skill-tags" style="margin:16px 0;">
                    <span class="skill-tag" x-text="selectedSkill?.category"></span>
                    <span class="skill-tag primary" x-text="'v' + selectedSkill?.version"></span>
                </div>
                <div class="form-label">SKILL.md Content</div>
                <div class="code-block" x-text="selectedSkill?.content"></div>
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px;">
                    <button class="btn-primary" @click="learnSkill(selectedSkill?.skill_id)">🧠 Learn This Skill</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ═══ Toast ═══ -->
    <div x-show="toast" x-transition class="toast">
        <span x-text="toast"></span>
    </div>

    <script>
    // ═══ WebGL — Fine Line Lattice Background ═══
    function initWebGL() {
        const canvas = document.getElementById('webgl-canvas');
        if (!canvas || typeof THREE === 'undefined') return;

        const scene = new THREE.Scene();
        const camera = new THREE.OrthographicCamera(
            window.innerWidth / -2, window.innerWidth / 2,
            window.innerHeight / 2, window.innerHeight / -2,
            1, 1000
        );
        camera.position.z = 10;

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Create lattice geometry
        const points = [];
        const gridSize = 30;
        const spacing = 40;

        for (let x = -gridSize; x <= gridSize; x += 5) {
            for (let y = -gridSize; y <= gridSize; y += 5) {
                points.push(x * spacing / gridSize, y * spacing / gridSize, 0);
            }
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));

        const material = new THREE.PointsMaterial({
            color: 0x00F0FF,
            size: 1.5,
            transparent: true,
            opacity: 0.4,
            blending: THREE.AdditiveBlending,
        });

        const lattice = new THREE.Points(geometry, material);
        scene.add(lattice);

        // Line connections
        const lineGeo = new THREE.BufferGeometry();
        const linePositions = [];
        for (let i = 0; i < points.length; i += 3) {
            for (let j = i + 3; j < Math.min(points.length, i + 30); j += 3) {
                const dx = points[i] - points[j];
                const dy = points[i+1] - points[j+1];
                if (Math.abs(dx) < 150 && Math.abs(dy) < 150) {
                    linePositions.push(points[i], points[i+1], points[i+2]);
                    linePositions.push(points[j], points[j+1], points[j+2]);
                }
            }
        }
        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        const lineMat = new THREE.LineBasicMaterial({ color: 0x00F0FF, transparent: true, opacity: 0.08 });
        const lines = new THREE.LineSegments(lineGeo, lineMat);
        scene.add(lines);

        // Animation — slow breathing pulse
        let time = 0;
        function animate() {
            requestAnimationFrame(animate);
            time += 0.005;

            lattice.rotation.z = Math.sin(time * 0.3) * 0.02;
            lines.rotation.z = Math.sin(time * 0.3) * 0.02;
            material.opacity = 0.3 + Math.sin(time) * 0.15;
            lineMat.opacity = 0.06 + Math.sin(time) * 0.04;

            renderer.render(scene, camera);
        }
        animate();

        // Resize
        window.addEventListener('resize', () => {
            camera.left = window.innerWidth / -2;
            camera.right = window.innerWidth / 2;
            camera.top = window.innerHeight / 2;
            camera.bottom = window.innerHeight / -2;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    document.addEventListener('DOMContentLoaded', initWebGL);

    // ═══ Alpine.js Marketplace ═══
    function marketplace() {
        return {
            view: 'home', skills: [], agents: [], stats: {},
            search: '', category: 'all',
            showPublishModal: false, selectedSkill: null,
            publishing: false, publishAgentId: '',
            toast: '', newSkill: { name: '', description: '', content: '', category: 'general' },

            async init() {
                await this.fetchStats();
                await this.fetchSkills();
                await this.fetchAgents();
                document.addEventListener('keydown', (e) => {
                    if (e.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) {
                        e.preventDefault(); document.querySelector('.search-box input')?.focus();
                    }
                    if (e.key === 'Escape') { this.showPublishModal = false; this.selectedSkill = null; }
                });
            },

            async fetchStats() { try { const r = await fetch('/api/v1/stats'); this.stats = await r.json(); } catch(e) {} },
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
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.newSkill),
                    });
                    if (r.ok) {
                        this.showToast('Skill published ✓');
                        this.showPublishModal = false;
                        this.newSkill = { name: '', description: '', content: '', category: 'general' };
                        await this.fetchSkills(); await this.fetchStats();
                    } else { this.showToast('Error: ' + ((await r.json()).detail || 'Unknown')); }
                } catch(e) { this.showToast('Publish failed'); }
                this.publishing = false;
            },

            async learnSkill(skillId) {
                if (!this.publishAgentId) { this.showToast('Set your Agent ID first'); return; }
                try {
                    const r = await fetch('/api/v1/agents/' + this.publishAgentId + '/learn', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ skill_id: skillId }),
                    });
                    if (r.ok) { this.showToast('Skill learned 🧠'); this.selectedSkill = null; await this.fetchStats(); }
                    else { this.showToast('Error: ' + ((await r.json()).detail || 'Unknown')); }
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
    return {"status": "ok", "service": "agent-self", "theme": "aether"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
