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
    # Startup
    init_db()
    print("🧠 Agent-Self started!")
    print("📚 Marketplace ready at http://localhost:8000")
    yield
    # Shutdown
    print("👋 Agent-Self shutting down...")


app = FastAPI(
    title="Agent-Self",
    description="Privacy-First Skill Marketplace for AI Agents",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(skills_router)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# === Web UI ===

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web UI."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Agent-Self</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
            50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8); }
        }
        .glow { animation: pulse-glow 2s infinite; }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen" x-data="marketplace()">
    
    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <span class="text-3xl">🧠</span>
                <div>
                    <h1 class="text-xl font-bold text-indigo-400">Agent-Self</h1>
                    <p class="text-xs text-gray-400">Privacy-First Skill Marketplace</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <button @click="showSubmitModal = true" 
                        class="bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg font-medium transition">
                    + Submit Skill
                </button>
            </div>
        </div>
    </header>

    <!-- Hero Stats -->
    <section class="bg-gradient-to-b from-indigo-900/30 to-gray-900 py-12">
        <div class="max-w-6xl mx-auto px-4">
            <div class="text-center mb-8">
                <h2 class="text-3xl font-bold mb-2">Learn Together, Grow Smarter</h2>
                <p class="text-gray-400">Verified skills • Trusted sources • Privacy preserved</p>
            </div>
            <div class="grid grid-cols-3 gap-4 max-w-lg mx-auto">
                <div class="bg-gray-800 rounded-xl p-4 text-center">
                    <div class="text-2xl font-bold text-indigo-400" x-text="stats.total_skills || '—'">—</div>
                    <div class="text-sm text-gray-400">Skills</div>
                </div>
                <div class="bg-gray-800 rounded-xl p-4 text-center">
                    <div class="text-2xl font-bold text-green-400" x-text="stats.approved_skills || '—'">—</div>
                    <div class="text-sm text-gray-400">Verified</div>
                </div>
                <div class="bg-gray-800 rounded-xl p-4 text-center">
                    <div class="text-2xl font-bold text-purple-400" x-text="stats.total_users || '—'">—</div>
                    <div class="text-sm text-gray-400">Agents</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Filter Bar -->
    <section class="max-w-6xl mx-auto px-4 py-6">
        <div class="flex flex-wrap gap-3 items-center">
            <input type="text" x-model="search" @input.debounce.300ms="fetchSkills()"
                   placeholder="Search skills..."
                   class="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 w-64 focus:border-indigo-500 focus:outline-none">
            
            <div class="flex gap-2">
                <template x-for="cat in ['all', ...stats.categories]" :key="cat">
                    <button @click="category = cat; fetchSkills()"
                            :class="category === cat ? 'bg-indigo-600' : 'bg-gray-700 hover:bg-gray-600'"
                            class="px-3 py-1 rounded-full text-sm capitalize transition"
                            x-text="cat">
                    </button>
                </template>
            </div>
        </div>
    </section>

    <!-- Skills Grid -->
    <main class="max-w-6xl mx-auto px-4 pb-12">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <template x-for="skill in skills" :key="skill.id">
                <div class="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-indigo-500 transition cursor-pointer"
                     @click="viewSkill(skill.slug)">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="font-semibold text-lg text-white" x-text="skill.name"></h3>
                        <div class="flex items-center gap-1 text-sm"
                             :class="skill.scan_result === 'clean' ? 'text-green-400' : skill.scan_result === 'suspicious' ? 'text-yellow-400' : 'text-red-400'">
                            <span x-text="skill.scan_result === 'clean' ? '✓' : skill.scan_result === 'suspicious' ? '⚠' : '✗'"></span>
                        </div>
                    </div>
                    <p class="text-gray-400 text-sm mb-4 line-clamp-2" x-text="skill.description"></p>
                    <div class="flex items-center justify-between text-sm">
                        <div class="flex gap-2">
                            <span class="bg-gray-700 px-2 py-0.5 rounded text-gray-300" x-text="skill.category"></span>
                            <span class="bg-indigo-900/50 px-2 py-0.5 rounded text-indigo-300" x-text="'v' + skill.version"></span>
                        </div>
                        <div class="flex items-center gap-1">
                            <span class="text-indigo-400 font-medium" x-text="skill.trust_score.toFixed(0)"></span>
                            <span class="text-gray-500">trust</span>
                        </div>
                    </div>
                </div>
            </template>
        </div>
        
        <!-- Empty State -->
        <div x-show="skills.length === 0" class="text-center py-12 text-gray-500">
            <div class="text-4xl mb-4">🔍</div>
            <p>No skills found. Be the first to submit!</p>
        </div>
    </main>

    <!-- Submit Modal -->
    <div x-show="showSubmitModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
         @click.self="showSubmitModal = false">
        <div class="bg-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="p-6 border-b border-gray-700">
                <h2 class="text-xl font-bold">Submit Skill</h2>
                <p class="text-gray-400 text-sm">Your skill will be scanned for security before publishing</p>
            </div>
            <div class="p-6 space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Skill Name</label>
                    <input type="text" x-model="newSkill.name" 
                           class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Description</label>
                    <textarea x-model="newSkill.description" rows="3"
                              class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Code (Python)</label>
                    <textarea x-model="newSkill.code" rows="10" 
                              class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 font-mono text-sm focus:border-indigo-500 focus:outline-none"
                              placeholder="# Your skill code here..."></textarea>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium mb-1">Category</label>
                        <select x-model="newSkill.category" 
                                class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none">
                            <template x-for="cat in stats.categories || []" :key="cat">
                                <option :value="cat" x-text="cat"></option>
                            </template>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-1">License</label>
                        <select x-model="newSkill.license"
                                class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none">
                            <option value="MIT">MIT</option>
                            <option value="Apache-2.0">Apache 2.0</option>
                            <option value="GPL-3.0">GPL 3.0</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="p-6 border-t border-gray-700 flex justify-end gap-3">
                <button @click="showSubmitModal = false" class="px-4 py-2 text-gray-400 hover:text-white">Cancel</button>
                <button @click="submitSkill()" :disabled="submitting"
                        class="bg-indigo-600 hover:bg-indigo-700 px-6 py-2 rounded-lg font-medium disabled:opacity-50">
                    <span x-show="!submitting">Submit & Scan</span>
                    <span x-show="submitting">Scanning...</span>
                </button>
            </div>
        </div>
    </div>

    <!-- Skill Detail Modal -->
    <div x-show="selectedSkill" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
         @click.self="selectedSkill = null">
        <div class="bg-gray-800 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto" x-show="selectedSkill">
            <div class="p-6 border-b border-gray-700 flex justify-between items-start">
                <div>
                    <h2 class="text-xl font-bold" x-text="selectedSkill?.name"></h2>
                    <p class="text-gray-400 text-sm">by <span x-text="selectedSkill?.author?.username"></span></p>
                </div>
                <button @click="selectedSkill = null" class="text-gray-400 hover:text-white text-2xl">&times;</button>
            </div>
            <div class="p-6 space-y-6">
                <p class="text-gray-300" x-text="selectedSkill?.description"></p>
                
                <!-- Trust & Security -->
                <div class="grid grid-cols-3 gap-4">
                    <div class="bg-gray-700 rounded-lg p-3 text-center">
                        <div class="text-2xl font-bold text-indigo-400" x-text="selectedSkill?.trust_score?.toFixed(0) + '%'"></div>
                        <div class="text-sm text-gray-400">Trust Score</div>
                    </div>
                    <div class="bg-gray-700 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold"
                             :class="selectedSkill?.scan_result === 'clean' ? 'text-green-400' : 'text-yellow-400'"
                             x-text="selectedSkill?.scan_result?.toUpperCase() || '—'"></div>
                        <div class="text-sm text-gray-400">Security</div>
                    </div>
                    <div class="bg-gray-700 rounded-lg p-3 text-center">
                        <div class="text-2xl font-bold text-purple-400" x-text="selectedSkill?.download_count || 0"></div>
                        <div class="text-sm text-gray-400">Downloads</div>
                    </div>
                </div>
                
                <!-- Tags -->
                <div class="flex flex-wrap gap-2">
                    <span class="bg-gray-700 px-3 py-1 rounded-full text-sm" x-text="selectedSkill?.category"></span>
                    <template x-for="tag in selectedSkill?.tags || []" :key="tag">
                        <span class="bg-indigo-900/50 px-3 py-1 rounded-full text-sm text-indigo-300" x-text="tag"></span>
                    </template>
                </div>
                
                <!-- Code Preview -->
                <div>
                    <h3 class="font-medium mb-2">Code</h3>
                    <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-sm"><code x-text="selectedSkill?.code"></code></pre>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast -->
    <div x-show="toast" x-transition 
         class="fixed bottom-6 right-6 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50"
         x-text="toast"></div>

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
            toast: '',
            newSkill: {
                name: '',
                description: '',
                code: '',
                category: 'general',
                license: 'MIT',
            },

            async init() {
                await this.fetchStats();
                await this.fetchSkills();
            },

            async fetchStats() {
                try {
                    const res = await fetch('/api/v1/stats');
                    this.stats = await res.json();
                } catch (e) {
                    console.error('Failed to fetch stats:', e);
                }
            },

            async fetchSkills() {
                try {
                    let url = '/api/v1.skills?status=approved';
                    if (this.category && this.category !== 'all') url += '&category=' + this.category;
                    if (this.search) url += '&search=' + encodeURIComponent(this.search);
                    const res = await fetch(url);
                    this.skills = await res.json();
                } catch (e) {
                    console.error('Failed to fetch skills:', e);
                }
            },

            async viewSkill(slug) {
                try {
                    const res = await fetch('/api/v1/skills/' + slug);
                    this.selectedSkill = await res.json();
                } catch (e) {
                    console.error('Failed to fetch skill:', e);
                }
            },

            async submitSkill() {
                if (!this.newSkill.name || !this.newSkill.code) {
                    this.showToast('Please fill in name and code');
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
                        this.showToast('Skill submitted and scanned! ✓');
                        this.showSubmitModal = false;
                        this.newSkill = { name: '', description: '', code: '', category: 'general', license: 'MIT' };
                        await this.fetchSkills();
                        await this.fetchStats();
                    } else {
                        const err = await res.json();
                        this.showToast('Error: ' + (err.detail || 'Unknown error'));
                    }
                } catch (e) {
                    this.showToast('Failed to submit skill');
                }
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
</html>
"""


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "agent-self"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
