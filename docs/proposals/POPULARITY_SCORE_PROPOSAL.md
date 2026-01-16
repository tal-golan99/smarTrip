# Popularity Score Integration Proposal

**Phase 2 Enhancement: Adding User Feedback Signals to Recommendation Scoring**

---

## Overview

Currently, the recommendation algorithm uses static criteria (budget, duration, themes, etc.) to score trips. This proposal adds **popularity signals** from real user behavior to improve recommendations.

---

## Data Sources (Already Implemented)

From Phase 1, we have:

| Table | Signals Available |
|-------|------------------|
| `trip_interactions` | impressions, clicks, saves, CTR |
| `events` | click_trip, save_trip, contact_whatsapp |

---

## Proposed Scoring Model

### Current Scoring (Max 100 points)

```
BASE_SCORE               25.0
THEME_FULL              +25.0
DIFFICULTY_PERFECT      +15.0
DURATION_IDEAL          +12.0
BUDGET_PERFECT          +12.0
STATUS_LAST_PLACES      +15.0
GEO_DIRECT_COUNTRY      +15.0
...
```

### New: Popularity Score Component (Max 10 points)

Add a new scoring component based on user engagement:

```python
POPULARITY_WEIGHTS = {
    # Click-through rate based
    'CTR_EXCELLENT': 5.0,      # CTR >= 15%
    'CTR_GOOD': 3.0,           # CTR >= 10%
    'CTR_AVERAGE': 1.0,        # CTR >= 5%
    
    # Trending boost (recent activity)
    'TRENDING_HOT': 5.0,       # 10+ clicks in 7 days
    'TRENDING_WARM': 3.0,      # 5-9 clicks in 7 days
    'TRENDING_NEW': 1.0,       # New trip (< 7 days old)
    
    # Conversion signals
    'HIGH_SAVE_RATE': 2.0,     # Save rate >= 20%
    'HIGH_CONTACT_RATE': 3.0,  # Contact rate >= 5%
}
```

---

## Implementation Details

### 1. Add Popularity Calculation Function

```python
def calculate_popularity_score(trip_id: int) -> tuple[float, list[str]]:
    """
    Calculate popularity score from trip_interactions.
    
    Returns:
        (score, match_details)
    """
    from database import db_session
    
    # Get interaction data
    interaction = db_session.execute(text("""
        SELECT 
            click_through_rate,
            clicks_7d,
            save_rate,
            contact_rate,
            created_at
        FROM trip_interactions 
        WHERE trip_id = :trip_id
    """), {'trip_id': trip_id}).fetchone()
    
    score = 0.0
    details = []
    
    if not interaction:
        return 0.0, []
    
    ctr = interaction[0] or 0
    clicks_7d = interaction[1] or 0
    save_rate = interaction[2] or 0
    contact_rate = interaction[3] or 0
    
    # CTR scoring
    if ctr >= 0.15:
        score += 5.0
        details.append(f"High Interest ({ctr*100:.0f}% CTR) [+5]")
    elif ctr >= 0.10:
        score += 3.0
        details.append(f"Good Interest ({ctr*100:.0f}% CTR) [+3]")
    elif ctr >= 0.05:
        score += 1.0
        details.append(f"Some Interest ({ctr*100:.0f}% CTR) [+1]")
    
    # Trending scoring
    if clicks_7d >= 10:
        score += 5.0
        details.append(f"Trending ({clicks_7d} recent clicks) [+5]")
    elif clicks_7d >= 5:
        score += 3.0
        details.append(f"Popular ({clicks_7d} recent clicks) [+3]")
    
    # Conversion signals
    if save_rate >= 0.20:
        score += 2.0
        details.append(f"Highly Saved [+2]")
    
    if contact_rate >= 0.05:
        score += 3.0
        details.append(f"High Contact Rate [+3]")
    
    return min(score, 10.0), details  # Cap at 10 points
```

### 2. Integrate Into Recommendation Algorithm

In `app.py`, after existing scoring:

```python
# ----------------------------------------
# 7. POPULARITY SCORING (NEW - Phase 2)
# ----------------------------------------
pop_score, pop_details = calculate_popularity_score(trip.id)
current_score += pop_score
match_details.extend(pop_details)
```

### 3. Update SCORING_WEIGHTS Constant

```python
SCORING_WEIGHTS = {
    # ... existing weights ...
    
    # NEW: Popularity weights
    'POPULARITY_CTR_EXCELLENT': 5.0,
    'POPULARITY_CTR_GOOD': 3.0,
    'POPULARITY_CTR_AVERAGE': 1.0,
    'POPULARITY_TRENDING_HOT': 5.0,
    'POPULARITY_TRENDING_WARM': 3.0,
    'POPULARITY_HIGH_SAVE': 2.0,
    'POPULARITY_HIGH_CONTACT': 3.0,
}
```

---

## Alternative: Weighted Hybrid Score

Instead of simple addition, use a weighted hybrid:

```python
def calculate_final_score(preference_score: float, popularity_score: float) -> float:
    """
    Combine preference matching with popularity.
    
    preference_score: 0-100 from existing algorithm
    popularity_score: 0-10 from user signals
    
    Returns: Final score 0-100
    """
    # Weight: 85% preference, 15% popularity
    PREFERENCE_WEIGHT = 0.85
    POPULARITY_WEIGHT = 0.15
    
    # Normalize popularity to 0-100 scale
    normalized_popularity = popularity_score * 10  # 0-10 -> 0-100
    
    final = (
        preference_score * PREFERENCE_WEIGHT +
        normalized_popularity * POPULARITY_WEIGHT
    )
    
    return min(100.0, max(0.0, final))
```

---

## Decay Function for Trending

Implement time decay for trending scores:

```python
def calculate_trending_score(clicks_7d: int, clicks_30d: int) -> float:
    """
    Calculate trending score with recency weighting.
    
    Recent clicks (7d) are worth more than older clicks (30d).
    """
    # 7-day clicks are full value
    recent_value = clicks_7d * 1.0
    
    # 8-30 day clicks are discounted 50%
    older_clicks = clicks_30d - clicks_7d
    older_value = older_clicks * 0.5
    
    total_weighted = recent_value + older_value
    
    if total_weighted >= 15:
        return 5.0  # Hot
    elif total_weighted >= 8:
        return 3.0  # Warm
    elif total_weighted >= 3:
        return 1.0  # Active
    return 0.0
```

---

## Cold Start Handling

New trips without interaction data need special handling:

```python
def get_popularity_score(trip_id: int, trip_created_at: date) -> tuple[float, list[str]]:
    """Handle trips with no interaction data."""
    
    interaction = get_trip_interactions(trip_id)
    
    if not interaction or interaction.impression_count < 10:
        # Not enough data - check if new trip
        days_since_created = (date.today() - trip_created_at).days
        
        if days_since_created <= 7:
            return 1.0, ["New Trip Bonus [+1]"]
        return 0.0, []
    
    # Normal popularity calculation
    return calculate_popularity_score(trip_id)
```

---

## Configuration Options

Add to `RecommendationConfig`:

```python
class RecommendationConfig:
    # ... existing config ...
    
    # Popularity settings
    POPULARITY_ENABLED = True              # Feature flag
    POPULARITY_MAX_POINTS = 10.0           # Max popularity contribution
    POPULARITY_CTR_THRESHOLDS = {
        'excellent': 0.15,
        'good': 0.10,
        'average': 0.05,
    }
    POPULARITY_TRENDING_THRESHOLDS = {
        'hot': 10,      # clicks in 7 days
        'warm': 5,
    }
    POPULARITY_MIN_IMPRESSIONS = 10        # Min data for scoring
    POPULARITY_WEIGHT = 0.15               # Weight in hybrid scoring
```

---

## Database Query Optimization

For performance, add index:

```sql
CREATE INDEX idx_trip_interactions_trip_id 
ON trip_interactions(trip_id);

CREATE INDEX idx_trip_interactions_clicks_7d 
ON trip_interactions(clicks_7d DESC);
```

---

## Display in Frontend

Add popularity indicators to trip cards:

```typescript
interface TripWithPopularity {
  id: number;
  // ... existing fields ...
  
  // Popularity signals
  popularity?: {
    isTrending: boolean;
    isPopular: boolean;
    clicksRecent: number;
  };
}

// In TripCard component:
{trip.popularity?.isTrending && (
  <span className="badge trending">Trending</span>
)}
{trip.popularity?.isPopular && (
  <span className="badge popular">Popular</span>
)}
```

---

## Testing Plan

1. **Unit Tests**
   - Test CTR thresholds
   - Test trending calculation
   - Test cold start handling

2. **Integration Tests**
   - Verify score changes with mock interactions
   - Test hybrid scoring math

3. **A/B Testing (Future)**
   - Compare recommendation quality with/without popularity
   - Measure click-through rates on recommendations

---

## Rollout Plan

1. **Phase 2a: Backend Only**
   - Add popularity calculation
   - Log scores but don't affect ranking
   - Analyze correlation with actual clicks

2. **Phase 2b: Gradual Integration**
   - Start with 5% weight (POPULARITY_WEIGHT = 0.05)
   - Monitor for feedback loops
   - Increase to 15% after validation

3. **Phase 2c: Full Integration**
   - Add trending badges to UI
   - Expose popularity signals in API

---

## Metrics to Monitor

| Metric | Target |
|--------|--------|
| Recommendation CTR | Increase by 10% |
| Time to first click | Decrease by 15% |
| Diversity of clicked trips | Maintain or improve |
| Cold start trip visibility | No decrease |

---

*Proposal created: December 16, 2025*
