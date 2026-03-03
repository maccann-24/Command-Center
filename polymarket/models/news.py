"""
BASED MONEY - News Event Model
Represents a news event from Twitter/RSS feeds
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class NewsEvent:
    """
    Represents a news event from external sources.

    Used by agents to detect market-moving information and calculate
    event impact on prediction markets.
    """

    # Unique identifier
    id: Optional[int] = None

    # Event timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # News headline/summary
    headline: str = ""

    # Extracted keywords (for market matching)
    keywords: List[str] = field(default_factory=list)

    # Source: 'twitter', 'reuters', 'ap', 'bloomberg', etc.
    source: str = ""

    # Sentiment score (-1.0 to 1.0, placeholder for v1)
    sentiment_score: float = 0.0

    # Original URL (if available)
    url: Optional[str] = None

    # Timestamp when saved to DB
    created_at: Optional[datetime] = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate news event fields"""
        if not -1.0 <= self.sentiment_score <= 1.0:
            raise ValueError(
                f"sentiment_score must be between -1.0 and 1.0, got {self.sentiment_score}"
            )

        # Normalize keywords to lowercase
        self.keywords = [kw.lower() for kw in self.keywords]

    def matches_keywords(self, target_keywords: List[str]) -> bool:
        """
        Check if this news event matches any target keywords.

        Args:
            target_keywords: List of keywords to match against

        Returns:
            True if any keyword overlaps
        """
        target_lower = [kw.lower() for kw in target_keywords]
        return any(kw in target_lower for kw in self.keywords)

    def extract_keywords_from_headline(self, keyword_list: List[str]) -> List[str]:
        """
        Extract keywords from headline text.

        Args:
            keyword_list: List of keywords to search for

        Returns:
            List of found keywords
        """
        headline_lower = self.headline.lower()
        found = []

        for keyword in keyword_list:
            if keyword.lower() in headline_lower:
                found.append(keyword.lower())

        return found

    def age_in_hours(self) -> float:
        """Calculate age of news event in hours"""
        delta = datetime.utcnow() - self.timestamp
        return delta.total_seconds() / 3600.0

    def is_recent(self, max_hours: int = 24) -> bool:
        """Check if news event is recent"""
        return self.age_in_hours() <= max_hours

    def to_dict(self) -> dict:
        """Convert news event to dictionary for database storage"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "headline": self.headline,
            "keywords": self.keywords,
            "source": self.source,
            "sentiment_score": float(self.sentiment_score),
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NewsEvent":
        """Create NewsEvent instance from dictionary"""
        # Convert ISO timestamp strings to datetime
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)

    def __repr__(self) -> str:
        """Human-readable representation"""
        return (
            f"NewsEvent(id={self.id}, source={self.source}, "
            f"headline='{self.headline[:60]}...', keywords={self.keywords[:3]}, "
            f"age={self.age_in_hours():.1f}h)"
        )
