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
        
    def reset(self) -> Email | None:
        self.current_idx = 0
        self.total_reward = 0.0
        return self.emails[self.current_idx] if self.emails else None
        
    def step(self, predicted: TriageResult) -> tuple[Email | None, float, bool, dict[str, Any]]:
        if self.current_idx >= self.max_steps:
            return None, 0.01, True, {"error": "Episode fully done"}
            
        current_email = self.emails[self.current_idx]
        email_id = predicted.email_id
        
        gt = LABELS.get(current_email.id)
        
        from env.graders import triage_grader
        reward = triage_grader(predicted, gt)
        self.total_reward += reward
        
        self.current_idx += 1
        done = self.current_idx >= self.max_steps
        next_email = self.emails[self.current_idx] if not done else None
        
        info = {"current_email_graded": email_id, "score": reward}
        return next_email, reward, done, info
        
    def current_observation(self) -> Email | None:
        return self.emails[self.current_idx] if self.current_idx < self.max_steps else None
        
    def state(self) -> dict[str, Any]:
        current_email = self.emails[self.current_idx] if self.current_idx < self.max_steps else None
        return {
            "current_email": current_email,
            "step_count": self.current_idx,
            "total_reward": self.total_reward,
            "done": self.current_idx >= self.max_steps
        }
