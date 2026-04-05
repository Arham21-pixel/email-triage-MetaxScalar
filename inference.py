"""
inference.py — Async inference script for Email Triage OpenEnv.

Runs a full 30-email episode against the HTTP API using an LLM-backed agent
and logs results in structured format.

Environment Variables
---------------------
API_BASE_URL : LLM API endpoint (default: https://router.huggingface.co/v1)
MODEL_NAME : LLM model name (default: Qwen/Qwen2.5-72B-Instruct)
HF_TOKEN : HuggingFace API token (required)
"""

from __future__ import annotations
import asyncio
import json
import os
import sys

import httpx
from openai import OpenAI


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN")
ENV_URL = "http://localhost:7860"
MAX_STEPS = 30
MAX_TOTAL_REWARD = 30.0
SUCCESS_SCORE_THRESHOLD = 0.5
TEMPERATURE = 0.0
MAX_TOKENS = 200
TASK_NAME = "email-triage"
BENCHMARK = "email-triage-env"


# ──────────────────────────────────────────────────────────────────────────────
# Logging functions
# ──────────────────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    """Log episode start."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str | None) -> None:
    """Log each step."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    """Log episode end."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)


# ──────────────────────────────────────────────────────────────────────────────
# System prompt
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an email triage agent.

Your task:
1. Classify the priority level: urgent, normal, or low
2. Classify the category: billing, support, spam, or inquiry
3. Write a short professional reply to the sender

Priority levels:
- urgent: requires action within 24 hours or causes active harm right now
- normal: requires action within a week
- low: informational, no action required, or obvious spam

Categories:
- billing: about invoices, payments, subscriptions, charges, refunds
- support: technical issues, bugs, help requests from existing users
- spam: unsolicited, promotional, phishing, or scam emails
- inquiry: questions, partnership requests, sales leads, press enquiries

You MUST return ONLY valid JSON with these keys:
{
    "priority": "urgent|normal|low",
    "category": "billing|support|spam|inquiry",
    "reply": "Your professional response here"
}

Do NOT include any text outside the JSON."""


# ──────────────────────────────────────────────────────────────────────────────
# Main inference
# ──────────────────────────────────────────────────────────────────────────────

async def run_inference() -> None:
    """Run full inference episode."""
    
    # Validate environment
    if not API_KEY:
        print("ERROR: HF_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    # Initialize clients
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    http_client = httpx.AsyncClient(timeout=30.0)
    
    try:
        # Reset environment
        reset_resp = await http_client.post(f"{ENV_URL}/reset")
        reset_resp.raise_for_status()
        reset_data = reset_resp.json()
        current_email = reset_data.get("first_email")
        
        step = 0
        rewards: list[float] = []
        
        # Main loop
        while current_email and step < MAX_STEPS:
            step += 1
            error = None
            reward = 0.0
            
            try:
                # Build user message
                user_msg = (
                    f"Subject: {current_email['subject']}\n"
                    f"From: {current_email['sender']}\n"
                    f"Date: {current_email['timestamp']}\n"
                    f"Task ID: {current_email['id']}\n\n"
                    f"{current_email['body']}"
                )
                
                # Call LLM
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                
                response_text = response.choices[0].message.content
                
                # Parse JSON
                action_json = json.loads(response_text)
                
                # Build action
                action = {
                    "email_id": current_email["id"],
                    "priority": action_json.get("priority", "normal"),
                    "category": action_json.get("category", "inquiry"),
                    "reply": action_json.get("reply", ""),
                }
                
                action_str = json.dumps(action)
                
                # Step environment
                step_resp = await http_client.post(
                    f"{ENV_URL}/step",
                    json=action,
                )
                step_resp.raise_for_status()
                step_data = step_resp.json()
                
                reward = step_data.get("reward", 0.0)
                done = step_data.get("done", False)
                current_email = step_data.get("observation")
                
                rewards.append(reward)
                log_step(step=step, action=action_str[:100], reward=reward, done=done, error=error)
                
                if done:
                    break
                
            except json.JSONDecodeError as e:
                error = f"JSON parse error: {str(e)}"
                rewards.append(0.0)
                log_step(step=step, action="error", reward=0.0, done=False, error=error)
            except Exception as e:
                error = f"Exception: {type(e).__name__}: {str(e)}"
                rewards.append(0.0)
                log_step(step=step, action="error", reward=0.0, done=False, error=error)
        
        # Calculate final score
        total_reward = sum(rewards)
        score = min(total_reward / MAX_TOTAL_REWARD, 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
        
        log_end(success=success, steps=step, score=score, rewards=rewards)
        
    finally:
        await http_client.aclose()


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(run_inference())
