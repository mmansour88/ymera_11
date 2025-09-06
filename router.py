
from typing import Tuple
def pick_provider_and_model(task_type: str, quality: str) -> Tuple[str,str]:
    policy = {
        ("general","balanced"): ("groq","llama-3.3-70b-versatile"),
        ("code","high"): ("anthropic","claude-3-7-sonnet-latest"),
        ("vision","balanced"): ("openai","gpt-4o-mini"),
        ("general","cheap"): ("deepseek","deepseek-chat"),
        ("tools","balanced"): ("openai","gpt-4o-mini")
    }
    return policy.get((task_type, quality), ("groq","llama-3.3-70b-versatile"))
