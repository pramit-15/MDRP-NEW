from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CurrentUser:
    """
    Represents the currently authenticated user in the system.
    Created from Clerk JWT payload.
    """
    user_id: str
    session_id: str
    email: str = ""
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.user_id)
