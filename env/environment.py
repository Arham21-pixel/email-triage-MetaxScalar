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
        
    def step(
        self,
        predicted: TriageResult,
        reward_override: float | None = None,
        task_name: str | None = None,
    ) -> tuple[Email | None, float, bool, dict[str, Any]]:
        if self.current_idx >= self.max_steps:
            return None, 0.01, True, {"error": "Episode fully done"}
            
        current_email = self.emails[self.current_idx]
        email_id = predicted.email_id
        
        gt = LABELS.get(current_email.id)
        
        from env.graders import task1_grader, task2_grader, task3_grader, triage_grader

        if reward_override is not None:
            reward = reward_override
        else:
            email_num = int(current_email.id.split("_")[1])
            if email_num <= 10:
                reward = task1_grader(predicted, gt)
                task_name = task_name or "task1"
            elif email_num <= 20:
                reward = task2_grader(predicted, gt)
                task_name = task_name or "task2"
            else:
                reward = task3_grader(predicted, gt)
                task_name = task_name or "task3"

        # Enforce strict validator bounds even if caller provides edge values.
        reward = min(max(float(reward), 0.01), 0.99)
        self.total_reward += reward
        
        self.current_idx += 1
        done = self.current_idx >= self.max_steps
        next_email = self.emails[self.current_idx] if not done else None
        
        info = {
            "current_email_graded": email_id,
            "score": reward,
            "task": task_name,
        }
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
