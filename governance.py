
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EscalationPolicy:
    orange_threshold: float = 0.4
    red_threshold: float = 0.7
    auto_shutdown_on_red: bool = True

DEFAULT = EscalationPolicy()

def grade_flag(risk_score: float, policy: EscalationPolicy = DEFAULT) -> str:
    if risk_score >= policy.red_threshold: return "red"
    if risk_score >= policy.orange_threshold: return "orange"
    return "green"


# Team suspension registry (in-memory; can be backed by DB later)
_team_status = {}  # team_id -> 'active' | 'suspended'

def suspend_team(team_id: int):
    _team_status[int(team_id)] = 'suspended'
    return {"team_id": int(team_id), "status": "suspended"}

def resume_team(team_id: int):
    _team_status[int(team_id)] = 'active'
    return {"team_id": int(team_id), "status": "active"}

def is_team_suspended(team_id: int) -> bool:
    return _team_status.get(int(team_id), 'active') == 'suspended'
