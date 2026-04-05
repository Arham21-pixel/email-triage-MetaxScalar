from __future__ import annotations
from typing import Any
from env.models import Email, TriageResult, Label
from env.tasks import EMAILS, LABELS
import random

class EmailTriageEnvironment:
    def __init__(self, shuffle: bool = False, seed: int = 42):
        self.emails = EMAILS.copy()
        if shuffle:
            random.seed(seed)
            random.shuffle(self.emails)
        
        self.current_idx = 0
        self.max_steps = len(self.emails)
        self.total_reward = 0.0
        
    def reset(self) -> dict[str, Any]:
        self.current_idx = 0
        self.total_reward = 0.0
        first_email = self.emails[self.current_idx] if self.emails else None
        return {
            "first_email": first_email
        }
        
    def step(self, action_dict: dict[str, Any]) -> dict[str, Any]:
        if self.current_idx >= self.max_steps:
            return {
                "observation": None,
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode fully done"}
            }
            
        current_email = self.emails[self.current_idx]
        email_id = action_dict.get("email_id")
        
        predicted = TriageResult(
            priority=action_dict.get("priority"),
            category=action_dict.get("category"),
            reply=action_dict.get("reply")
        )
        
        gt = LABELS.get(current_email.id)
        
        from env.graders import triage_grader
        reward = triage_grader(predicted, gt)
        self.total_reward += reward
        
        self.current_idx += 1
        done = self.current_idx >= self.max_steps
        next_email = self.emails[self.current_idx] if not done else None
        
        return {
            "observation": next_email,
            "reward": reward,
            "done": done,
            "info": {"current_email_graded": email_id, "score": reward}
        }
        
    def state(self) -> dict[str, Any]:
        current_email = self.emails[self.current_idx] if self.current_idx < self.max_steps else None
        return {
            "current_email": current_email,
            "step_count": self.current_idx,
            "total_reward": self.total_reward,
            "done": self.current_idx >= self.max_steps
        }
