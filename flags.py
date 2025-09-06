from enum import Enum
class Flag(str, Enum):
    GREEN="green"
    ORANGE="orange"
    RED="red"

def compute_flag(score: float, errors:int=0) -> Flag:
    if score < 0.4 or errors>3: return Flag.RED
    if score < 0.7 or errors>0: return Flag.ORANGE
    return Flag.GREEN
