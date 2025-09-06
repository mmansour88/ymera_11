
from typing import Dict, Any

class LLMProvider:
    name: str = "base"
    def __init__(self): ...
    async def chat(self, messages: list[dict], model: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
    def estimate_cost(self, tokens_in: int, tokens_out: int, model: str) -> float:
        # Minimal heuristics; refine with real pricing tables
        return 0.000002 * tokens_in + 0.000006 * tokens_out
