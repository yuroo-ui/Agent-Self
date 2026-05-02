"""Trust Score Engine - Calculate and manage skill/author trust scores.

Trust Score Factors:
1. Security scan results (40%)
2. Community reviews (25%)
3. Usage statistics (15%)
4. Author reputation (10%)
5. Maintenance activity (10%)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class TrustFactors:
    """Individual trust factors for calculation."""
    security_score: float = 100.0    # From scan results (0-100)
    review_score: float = 50.0       # From reviews (0-100)
    usage_score: float = 0.0         # From download/usage count (0-100)
    author_score: float = 50.0       # From author reputation (0-100)
    maintenance_score: float = 50.0  # From update frequency (0-100)


# Weights for trust score calculation
WEIGHTS = {
    "security": 0.40,
    "review": 0.25,
    "usage": 0.15,
    "author": 0.10,
    "maintenance": 0.10,
}


class TrustEngine:
    """Calculate trust scores for skills and authors."""
    
    def calculate_skill_trust_score(
        self,
        security_scan_result: str,  # clean, suspicious, malicious
        security_trust_score: float,  # 0-100 from scanner
        avg_rating: float,  # 0-5 from reviews
        review_count: int,
        download_count: int,
        usage_count: int,
        author_reputation: float,  # 0-100
        days_since_update: int,
        fork_count: int = 0,
    ) -> float:
        """Calculate overall trust score for a skill (0-100)."""
        
        # Security score (0-100)
        security = self._calc_security_score(security_scan_result, security_trust_score)
        
        # Review score (0-100)
        review = self._calc_review_score(avg_rating, review_count)
        
        # Usage score (0-100)
        usage = self._calc_usage_score(download_count, usage_count, fork_count)
        
        # Author score (0-100)
        author = min(100.0, author_reputation)
        
        # Maintenance score (0-100)
        maintenance = self._calc_maintenance_score(days_since_update)
        
        # Weighted sum
        total = (
            security * WEIGHTS["security"] +
            review * WEIGHTS["review"] +
            usage * WEIGHTS["usage"] +
            author * WEIGHTS["author"] +
            maintenance * WEIGHTS["maintenance"]
        )
        
        return round(max(0.0, min(100.0, total)), 1)
    
    def _calc_security_score(self, scan_result: str, trust_score: float) -> float:
        """Security score based on scan results."""
        multipliers = {
            "clean": 1.0,
            "suspicious": 0.5,
            "malicious": 0.0,
        }
        return trust_score * multipliers.get(scan_result, 0.0)
    
    def _calc_review_score(self, avg_rating: float, review_count: int) -> float:
        """Review score with confidence based on count."""
        if review_count == 0:
            return 50.0  # Neutral when no reviews
        
        # Normalize rating to 0-100
        rating_score = (avg_rating / 5.0) * 100.0
        
        # Confidence factor (more reviews = more confidence)
        # Uses logarithmic scaling: 1 review = 0.3, 10 = 0.7, 100 = 1.0
        import math
        confidence = min(1.0, math.log10(review_count + 1) / 2.0)
        
        # Blend neutral (50) with actual rating based on confidence
        return 50.0 * (1 - confidence) + rating_score * confidence
    
    def _calc_usage_score(self, downloads: int, usage: int, forks: int) -> float:
        """Usage score based on adoption metrics."""
        import math
        
        # Logarithmic scaling (1000 downloads ≈ 70 points)
        download_score = min(100.0, math.log10(max(1, downloads)) * 20)
        usage_score = min(100.0, math.log10(max(1, usage)) * 25)
        fork_score = min(100.0, math.log10(max(1, forks + 1)) * 30)
        
        return (download_score * 0.4 + usage_score * 0.4 + fork_score * 0.2)
    
    def _calc_maintenance_score(self, days_since_update: int) -> float:
        """Maintenance score based on update recency."""
        if days_since_update <= 7:
            return 100.0
        elif days_since_update <= 30:
            return 80.0
        elif days_since_update <= 90:
            return 60.0
        elif days_since_update <= 180:
            return 40.0
        elif days_since_update <= 365:
            return 20.0
        else:
            return 10.0
    
    def calculate_author_reputation(
        self,
        total_skills: int,
        avg_skill_rating: float,
        verified: bool,
        account_age_days: int,
        total_downloads: int,
    ) -> float:
        """Calculate author reputation score (0-100)."""
        import math
        
        score = 50.0  # Base score
        
        # Verified bonus
        if verified:
            score += 15.0
        
        # Skills contribution
        score += min(15.0, total_skills * 1.5)
        
        # Rating contribution
        if total_skills > 0:
            score += (avg_skill_rating / 5.0) * 10.0
        
        # Age factor (trust builds over time)
        age_factor = min(1.0, math.log10(max(1, account_age_days)) / 2.0)
        score += age_factor * 10.0
        
        return round(max(0.0, min(100.0, score)), 1)


# Singleton
trust_engine = TrustEngine()
