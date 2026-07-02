from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class Asset:

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    page_number: int = 0

    bbox: Optional[List[int]] = None

    image: Any = None

    mask: Any = None

    confidence: float = 0.0

    source: str = ""

    quality_score: float = 0.0

    certified: bool = False

    rejected: bool = False

    rejection_reason: str = ""

    metadata: Dict = field(default_factory=dict)


@dataclass
class RecoveryPage:

    page_number: int

    page_width: int

    page_height: int

    page_image: Any

    assets: List[Asset] = field(default_factory=list)

    metadata: Dict = field(default_factory=dict)