"""
api/main.py — FastAPI service for the Email Triage OpenEnv environment.

Endpoints
---------
GET  /                → landing page
GET  /healthz         → liveness probe with environment info
POST /reset           → reset environment, return first email
POST /step            → submit action, step environment
GET  /state           → return current environment state
GET  /emails          → list all 30 emails
GET  /docs            → automatic Swagger UI
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from env.models import Email, Label, TriageResult, Priority, Category
from env.environment import EmailTriageEnvironment
from env.graders import task1_grader, task2_grader, task3_grader

# ──────────────────────────────────────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Email Triage OpenEnv API",
    description="REST API for the Email Triage OpenEnv benchmark environment.",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared environment instance
_env = EmailTriageEnvironment(shuffle=False)


# ──────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ──────────────────────────────────────────────────────────────────────────────

class EmailAction(BaseModel):
    email_id: str
    priority: Priority
    category: Category
    reply: str | None = None
    reasoning: str | None = None


class StepResponse(BaseModel):
    observation: Email | None
    reward: float
    done: bool
    info: dict


class StateResponse(BaseModel):
    current_email: Email | None
    step_count: int
    total_reward: float
    done: bool


class ResetResponse(BaseModel):
    status: str
    first_email: Email


class HealthResponse(BaseModel):
    status: str
    environment: str


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["Root"])
def root():
    """Modern SaaS landing page for Email Triage OpenEnv."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Triage OpenEnv — LLM Benchmark</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --surface: #0f0f0f;
            --text: #ffffff;
            --text-muted: #666666;
            --text-secondary: #999999;
            --purple: #7c3aed;
            --green: #10b981;
            --amber: #f59e0b;
            --red: #ef4444;
            --blue: #3b82f6;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            animation: fadein 0.5s ease forwards;
        }

        @keyframes fadein {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        .container {
            max-width: 1080px;
            margin: 0 auto;
            padding: 0 24px;
        }

        /* Navbar */
        nav {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: rgba(5, 5, 5, 0.85);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid #1a1a1a;
            z-index: 100;
            display: flex;
            align-items: center;
        }

        nav .container {
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-dot {
            width: 8px;
            height: 8px;
            background: var(--purple);
            border-radius: 50%;
        }

        .nav-brand-text {
            color: var(--text);
            font-size: 14px;
            font-weight: 500;
        }

        .nav-version {
            background: #1a1a1a;
            color: var(--text-muted);
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 12px;
            margin-left: 8px;
        }

        .nav-links {
            display: flex;
            gap: 32px;
            list-style: none;
        }

        .nav-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s;
        }

        .nav-links a:hover {
            color: var(--text);
        }

        main {
            margin-top: 60px;
        }

        /* Hero */
        .hero {
            padding: 180px 0 120px;
            text-align: center;
            background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124, 58, 237, 0.15), transparent);
        }

        .hero h1 {
            font-size: 64px;
            font-weight: 700;
            line-height: 1.05;
            letter-spacing: -2px;
            color: var(--text);
            margin-bottom: 24px;
        }

        .hero h1 .accent {
            color: var(--purple);
        }

        .hero p {
            font-size: 18px;
            color: var(--text-muted);
            max-width: 480px;
            margin: 0 auto 48px;
            line-height: 1.7;
        }

        .hero-buttons {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }

        .btn {
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            border: none;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background 0.2s, transform 0.1s, border-color 0.2s, color 0.2s;
        }

        .btn-primary {
            background: var(--purple);
            color: white;
        }

        .btn-primary:hover {
            background: #6d28d9;
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid #222;
        }

        .btn-secondary:hover {
            border-color: #444;
            color: var(--text);
        }

        /* Metrics Strip */
        .metrics {
            margin-top: 80px;
            border-top: 1px solid #1a1a1a;
            border-bottom: 1px solid #1a1a1a;
            padding: 48px 0;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            text-align: center;
        }

        .metric {
            border-right: 1px solid #1a1a1a;
            padding: 0 40px;
        }

        .metric:last-child {
            border-right: none;
        }

        .metric-number {
            font-size: 40px;
            font-weight: 700;
            color: var(--text);
            letter-spacing: -1px;
        }

        .metric-label {
            font-size: 13px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 6px;
            font-weight: 500;
        }

        /* Tasks Section */
        .tasks-section {
            padding: 120px 0;
        }

        .section-header {
            margin-bottom: 64px;
        }

        .section-eyebrow {
            font-size: 11px;
            color: var(--purple);
            letter-spacing: 0.15em;
            text-transform: uppercase;
            font-weight: 500;
        }

        .section-header h2 {
            font-size: 40px;
            font-weight: 700;
            letter-spacing: -1px;
            margin-top: 12px;
            color: var(--text);
        }

        .section-header p {
            font-size: 16px;
            color: var(--text-muted);
            margin-top: 12px;
            max-width: 460px;
        }

        .tasks {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .task-card {
            background: var(--surface);
            border: 1px solid #1f1f1f;
            border-radius: 16px;
            padding: 32px;
            transition: border-color 0.2s, transform 0.2s;
        }

        .task-card:hover {
            border-color: #333;
            transform: translateY(-3px);
        }

        .task-card.featured {
            border-color: rgba(124, 58, 237, 0.25);
        }

        .task-card.featured:hover {
            border-color: rgba(124, 58, 237, 0.5);
        }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .task-tier {
            font-size: 11px;
            color: #444;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 500;
        }

        .task-badge {
            border-radius: 100px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 500;
            border: 1px solid;
        }

        .badge-easy {
            background: rgba(16, 185, 129, 0.1);
            color: var(--green);
            border-color: rgba(16, 185, 129, 0.25);
        }

        .badge-medium {
            background: rgba(245, 158, 11, 0.1);
            color: var(--amber);
            border-color: rgba(245, 158, 11, 0.25);
        }

        .badge-hard {
            background: rgba(239, 68, 68, 0.1);
            color: var(--red);
            border-color: rgba(239, 68, 68, 0.25);
        }

        .task-card h3 {
            font-size: 20px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 10px;
        }

        .task-card > p {
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 24px;
        }

        .task-divider {
            border-top: 1px solid #1a1a1a;
            margin: 24px 0;
        }

        .task-code {
            background: #080808;
            border: 1px solid #1a1a1a;
            border-radius: 8px;
            padding: 14px 16px;
            font-family: monospace;
            font-size: 13px;
            color: var(--purple);
            overflow-x: auto;
        }

        .task-footer {
            margin-top: 20px;
            font-size: 13px;
            color: #444;
        }

        /* API Section */
        .api-section {
            background: #080808;
            padding: 120px 0;
            border-top: 1px solid #1a1a1a;
            border-bottom: 1px solid #1a1a1a;
        }

        .api-table {
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 48px;
        }

        .api-table thead {
            background: var(--surface);
        }

        .api-table th {
            padding: 14px 24px;
            font-size: 11px;
            color: #444;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            border-bottom: 1px solid #1a1a1a;
            text-align: left;
            font-weight: 600;
        }

        .api-table td {
            padding: 18px 24px;
            border-bottom: 1px solid #111;
            font-size: 14px;
        }

        .api-table tbody tr:hover {
            background: var(--surface);
            transition: background 0.15s;
        }

        .api-table tbody tr:last-child td {
            border-bottom: none;
        }

        .method-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            font-family: monospace;
            border: 1px solid;
        }

        .method-post {
            background: rgba(59, 130, 246, 0.1);
            color: var(--blue);
            border-color: rgba(59, 130, 246, 0.25);
        }

        .method-get {
            background: rgba(16, 185, 129, 0.1);
            color: var(--green);
            border-color: rgba(16, 185, 129, 0.25);
        }

        .endpoint {
            font-family: monospace;
            font-size: 14px;
            color: #ccc;
            padding-left: 16px;
        }

        .api-description {
            font-size: 14px;
            color: var(--text-muted);
        }

        /* Reward Section */
        .reward-section {
            padding: 120px 0;
        }

        .rewards {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 640px;
            margin: 48px auto 0;
        }

        .reward-card {
            display: flex;
            align-items: center;
            gap: 24px;
            padding: 24px 28px;
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid #1a1a1a;
            border-left: 3px solid;
        }

        .reward-score-box {
            width: 64px;
            height: 48px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
            flex-shrink: 0;
        }

        .reward-score-perfect {
            background: rgba(16, 185, 129, 0.1);
            color: var(--green);
        }

        .reward-score-partial {
            background: rgba(245, 158, 11, 0.1);
            color: var(--amber);
        }

        .reward-score-zero {
            background: rgba(239, 68, 68, 0.1);
            color: var(--red);
        }

        .reward-text h4 {
            font-size: 15px;
            font-weight: 500;
            color: var(--text);
        }

        .reward-text p {
            font-size: 14px;
            color: var(--text-muted);
            margin-top: 3px;
        }

        .reward-card.perfect {
            border-left-color: var(--green);
        }

        .reward-card.partial {
            border-left-color: var(--amber);
        }

        .reward-card.zero {
            border-left-color: var(--red);
        }

        /* Footer */
        footer {
            padding: 36px 0;
            border-top: 1px solid #111;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            color: #333;
        }

        .footer-left {
            color: var(--text);
            font-weight: 500;
        }

        .footer-left .version {
            color: #333;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            .tasks {
                grid-template-columns: repeat(2, 1fr);
            }

            .metrics {
                grid-template-columns: repeat(2, 1fr);
            }

            .metric {
                border-right: none;
                border-bottom: 1px solid #1a1a1a;
                padding: 24px 40px;
            }

            .metric:nth-child(even) {
                border-right: none;
            }

            .metric:nth-child(3),
            .metric:nth-child(4) {
                border-bottom: none;
            }
        }

        @media (max-width: 768px) {
            .container {
                padding: 0 20px;
            }

            .hero {
                padding: 120px 0 80px;
            }

            .hero h1 {
                font-size: 42px;
            }

            .hero p {
                font-size: 16px;
            }

            .hero-buttons {
                flex-direction: column;
            }

            .btn {
                width: 100%;
            }

            .tasks {
                grid-template-columns: 1fr;
            }

            .metrics {
                grid-template-columns: 1fr;
            }

            .metric {
                border-right: none;
                border-bottom: 1px solid #1a1a1a;
                padding: 24px 0;
            }

            .metric:last-child {
                border-bottom: none;
            }

            .section-header h2 {
                font-size: 32px;
            }

            .api-table {
                overflow-x: auto;
                display: block;
            }

            footer {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }
        }
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <div class="nav-brand">
                <div class="nav-dot"></div>
                <span class="nav-brand-text">email-triage-env</span>
                <span class="nav-version">v1.0.0</span>
            </div>
            <ul class="nav-links">
                <li><a href="/docs">API Docs</a></li>
                <li><a href="/emails">Emails</a></li>
            </ul>
        </div>
    </nav>

    <main>
        <!-- Hero -->
        <section class="hero">
            <div class="container">
                <h1>Email Triage<br><span class="accent">Environment</span></h1>
                <p>A production-grade benchmark for evaluating LLM agents on real-world email triage tasks.</p>
                <div class="hero-buttons">
                    <a href="/docs" class="btn btn-primary">Explore API Docs</a>
                    <a href="/emails" class="btn btn-secondary">View Emails</a>
                </div>
            </div>
        </section>

        <!-- Metrics -->
        <div class="metrics">
            <div class="metric">
                <div class="metric-number">30</div>
                <div class="metric-label">Email Scenarios</div>
            </div>
            <div class="metric">
                <div class="metric-number">3</div>
                <div class="metric-label">Difficulty Tiers</div>
            </div>
            <div class="metric">
                <div class="metric-number">4</div>
                <div class="metric-label">Action Categories</div>
            </div>
            <div class="metric">
                <div class="metric-number">1.0</div>
                <div class="metric-label">Max Reward</div>
            </div>
        </div>

        <!-- Tasks -->
        <section class="tasks-section">
            <div class="container">
                <div class="section-header">
                    <div class="section-eyebrow">Evaluation</div>
                    <h2>Benchmark Tasks</h2>
                    <p>Three progressive tiers with deterministic, reproducible graders</p>
                </div>

                <div class="tasks">
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-tier">Tier 1</div>
                            <div class="task-badge badge-easy">Easy</div>
                        </div>
                        <h3>Priority Classification</h3>
                        <p>Classify each email as urgent, normal, or low priority based on content signals.</p>
                        <div class="task-divider"></div>
                        <div class="task-code">reward = 1.0 if priority_correct else 0.0</div>
                        <div class="task-footer">10 email scenarios</div>
                    </div>

                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-tier">Tier 2</div>
                            <div class="task-badge badge-medium">Medium</div>
                        </div>
                        <h3>Priority + Category</h3>
                        <p>Dual-axis classification across billing, support, spam, and inquiry categories.</p>
                        <div class="task-divider"></div>
                        <div class="task-code">reward = 0.5 × priority + 0.5 × category</div>
                        <div class="task-footer">10 email scenarios</div>
                    </div>

                    <div class="task-card featured">
                        <div class="task-header">
                            <div class="task-tier">Tier 3</div>
                            <div class="task-badge badge-hard">Hard</div>
                        </div>
                        <h3>Full Triage + Reply</h3>
                        <p>Complete triage pipeline with professional reply generation evaluated for quality.</p>
                        <div class="task-divider"></div>
                        <div class="task-code">reward = 0.3p + 0.3c + 0.4 × reply_quality</div>
                        <div class="task-footer">10 email scenarios</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- API -->
        <section class="api-section">
            <div class="container">
                <div class="section-header">
                    <div class="section-eyebrow">Interface</div>
                    <h2>API Reference</h2>
                    <p>RESTful endpoints — fully OpenEnv spec compliant</p>
                </div>

                <table class="api-table">
                    <thead>
                        <tr>
                            <th style="width: 120px;">Method</th>
                            <th style="width: 200px;">Endpoint</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="method-badge method-post">POST</span></td>
                            <td><span class="endpoint">/reset</span></td>
                            <td class="api-description">Initialize episode, returns first email</td>
                        </tr>
                        <tr>
                            <td><span class="method-badge method-post">POST</span></td>
                            <td><span class="endpoint">/step</span></td>
                            <td class="api-description">Submit action, receive reward + observation</td>
                        </tr>
                        <tr>
                            <td><span class="method-badge method-get">GET</span></td>
                            <td><span class="endpoint">/state</span></td>
                            <td class="api-description">Query current environment state</td>
                        </tr>
                        <tr>
                            <td><span class="method-badge method-get">GET</span></td>
                            <td><span class="endpoint">/healthz</span></td>
                            <td class="api-description">Liveness probe and environment info</td>
                        </tr>
                        <tr>
                            <td><span class="method-badge method-get">GET</span></td>
                            <td><span class="endpoint">/emails</span></td>
                            <td class="api-description">List all 30 benchmark scenarios</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Rewards -->
        <section class="reward-section">
            <div class="container">
                <div class="section-header">
                    <div class="section-eyebrow">Scoring</div>
                    <h2>Reward Function</h2>
                    <p>Dense reward shaping with partial credit signals</p>
                </div>

                <div class="rewards">
                    <div class="reward-card perfect">
                        <div class="reward-score-box reward-score-perfect">1.0</div>
                        <div class="reward-text">
                            <h4>Full Score</h4>
                            <p>Both priority and category classified correctly</p>
                        </div>
                    </div>
                    <div class="reward-card partial">
                        <div class="reward-score-box reward-score-partial">0.5</div>
                        <div class="reward-text">
                            <h4>Partial Credit</h4>
                            <p>One dimension correct — priority or category</p>
                        </div>
                    </div>
                    <div class="reward-card zero">
                        <div class="reward-score-box reward-score-zero">0.0</div>
                        <div class="reward-text">
                            <h4>No Score</h4>
                            <p>Both dimensions classified incorrectly</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="container">
            <div class="footer-left">
                email-triage-env <span class="version">— v1.0.0</span>
            </div>
            <div>OpenEnv Hackathon · Meta × Hugging Face</div>
        </footer>
    </main>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/healthz", response_model=HealthResponse, tags=["Infra"])
def healthz():
    """Health check endpoint."""
    return {
        "status": "ok",
        "environment": "email-triage-env",
    }


@app.post("/reset", response_model=ResetResponse, tags=["Environment"])
def reset():
    """Reset the environment and return the first email."""
    first_email = _env.reset()
    return {
        "status": "reset",
        "first_email": first_email,
    }


@app.post("/step", response_model=StepResponse, tags=["Environment"])
def step(action: EmailAction):
    """
    Submit an action (classification + optional reply) and step the environment.
    
    Returns observation, reward, done, and info dict.
    """
    current = _env.current_observation()
    if current is None:
        raise HTTPException(
            status_code=409,
            detail="Episode complete. Call POST /reset to start a new episode.",
        )
    
    if current.id != action.email_id:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Expected email_id='{current.id}', "
                f"but got '{action.email_id}'. "
                "Submit predictions in order."
            ),
        )
    
    # Create prediction
    prediction = TriageResult(
        email_id=action.email_id,
        priority=action.priority,
        category=action.category,
        reply=action.reply,
        reasoning=action.reasoning,
    )
    
    # Get ground truth and compute reward using task-specific grader.
    from env.tasks import LABELS
    ground_truth = LABELS[action.email_id]
    email_num = int(action.email_id.split("_")[1])
    if email_num <= 10:
        reward = task1_grader(prediction, ground_truth)
        task_name = "task1"
    elif email_num <= 20:
        reward = task2_grader(prediction, ground_truth)
        task_name = "task2"
    else:
        reward = task3_grader(prediction, ground_truth)
        task_name = "task3"
    
    # Step environment
    next_obs, reward, done, info = _env.step(
        prediction,
        reward_override=reward,
        task_name=task_name,
    )
    
    return {
        "observation": next_obs,
        "reward": reward,
        "done": done,
        "info": {
            "email_id": action.email_id,
            "task": task_name,
            "ground_truth": ground_truth.model_dump(),
            **info,
        },
    }


@app.get("/state", response_model=StateResponse, tags=["Environment"])
def get_state():
    """Return the current environment state."""
    return _env.state()


@app.get("/emails", response_model=list[Email], tags=["Tasks"])
def list_emails():
    """Return all 30 task emails."""
    from env.tasks import EMAILS
    return EMAILS


@app.get("/emails/{email_id}", response_model=Email, tags=["Tasks"])
def get_email(email_id: str):
    """Return a single email by ID."""
    from env.tasks import EMAILS
    for email in EMAILS:
        if email.id == email_id:
            return email
    raise HTTPException(status_code=404, detail=f"Email '{email_id}' not found.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=True)
