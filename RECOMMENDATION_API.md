# SmartTrip Recommendation Engine API

## Overview

The SmartTrip recommendation engine uses a **Weighted Scoring Algorithm** that evaluates trips on a **0-100 point scale** based on user preferences. The system respects the strict separation between **TYPE** (trip style) and **THEME** (trip content) tags.

---

## Endpoint

```
POST /api/recommendations
```

---

## Request Format

### Headers
```
Content-Type: application/json
```

### Request Body

```json
{
  "selected_countries": [12, 15],     // Optional: List of country IDs
  "selected_continents": ["Asia"],    // Optional: List of continent names
  
  "preferred_type_id": 5,             // Optional: Single TYPE tag ID (trip style)
  "preferred_theme_ids": [10, 12],    // Optional: Up to 3 THEME tag IDs (trip interests)
  
  "min_duration": 7,                  // Optional: Minimum trip duration in days
  "max_duration": 14,                 // Optional: Maximum trip duration in days
  "budget": 5000,                     // Optional: Maximum budget in ILS/USD
  "difficulty": 2,                    // Optional: 1=Easy, 2=Moderate, 3=Hard
  "start_date": "2025-01-01"          // Optional: Earliest desired start date (YYYY-MM-DD)
}
```

### Field Details

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `selected_countries` | `number[]` | No | Array of country IDs to filter by |
| `selected_continents` | `string[]` | No | Array of continent names ("Africa", "Asia", "Europe", etc.) |
| `preferred_type_id` | `number` | No | The ID of ONE TYPE tag (trip style like "Safari", "Train Tours") |
| `preferred_theme_ids` | `number[]` | No | Array of 1-3 THEME tag IDs (interests like "Wildlife", "Cultural") |
| `min_duration` | `number` | No | Minimum acceptable trip duration in days |
| `max_duration` | `number` | No | Maximum acceptable trip duration in days |
| `budget` | `number` | No | Maximum budget willing to spend |
| `difficulty` | `number` | No | Preferred difficulty level (1, 2, or 3) |
| `start_date` | `string` | No | Earliest acceptable departure date in ISO format |

---

## Algorithm Logic

### Step 1: Hard Filtering (Pass/Fail)

The system first applies strict filters to eliminate non-matching trips:

1. **Geography**: Trip must be in `selected_countries` OR `selected_continents` (if specified)
2. **Date**: Trip `start_date` must be >= user's `start_date` (if specified)
3. **Availability**: Trip status != "Cancelled" AND `spots_left` > 0

### Step 2: Weighted Scoring (0-100 Points)

Each remaining trip is scored across 6 dimensions:

#### 1. TYPE Match (Max 25 points) - "Trip Style"
- **25 pts**: Trip has the exact TYPE tag user selected
- **0 pts**: No TYPE match

*Example*: User wants "Safari", trip has "Safari" TYPE tag → 25 pts

#### 2. THEME Match (Max 15 points) - "Trip Content"
- **15 pts**: Trip has 2+ matching THEME tags
- **7 pts**: Trip has 1 matching THEME tag
- **0 pts**: No THEME matches

*Example*: User wants "Wildlife" + "Photography", trip has both → 15 pts

#### 3. Difficulty Match (Max 20 points)
- **20 pts**: Exact match (user wants 2, trip is 2)
- **10 pts**: Deviation of 1 level (user wants 2, trip is 1 or 3)
- **0 pts**: Deviation of 2 levels (user wants 1, trip is 3)

#### 4. Duration Match (Max 15 points)
- **15 pts**: Trip duration within user's range
- **10 pts**: Small deviation (±2 days)
- **5 pts**: Medium deviation (±5 days)
- **0 pts**: Large deviation

*Example*: User wants 7-14 days, trip is 10 days → 15 pts

#### 5. Budget Match (Max 15 points)
- **15 pts**: Trip price ≤ user's budget
- **10 pts**: Price ≤ 110% of budget
- **5 pts**: Price ≤ 120% of budget
- **0 pts**: Price > 120% of budget

#### 6. Business Logic (Max 10 points)
- **10 pts**: Trip status is "Guaranteed" or "Last Places"
- **5 pts**: Trip departs within 45 days
- **0 pts**: Neither applies

### Step 3: Ranking & Response

- Trips are sorted by `match_score` (descending)
- Top 10 trips are returned
- Each trip includes `match_score` and `match_details`

---

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "count": 10,
  "total_candidates": 45,
  "data": [
    {
      "id": 123,
      "title": "Wildlife Safari in Kenya",
      "titleHe": "ספארי בקניה",
      "description": "...",
      "startDate": "2025-03-15",
      "endDate": "2025-03-25",
      "price": 12000,
      "status": "Guaranteed",
      "difficultyLevel": 2,
      "spotsLeft": 8,
      "maxCapacity": 20,
      
      "country": { "id": 7, "name": "Kenya", "continent": "Africa" },
      "guide": { "id": 2, "name": "David Levi", "email": "..." },
      "tags": [
        { "id": 4, "name": "African Safari", "category": "Type" },
        { "id": 14, "name": "Wildlife", "category": "Theme" },
        { "id": 12, "name": "Photography", "category": "Theme" }
      ],
      
      "match_score": 87,
      "match_details": [
        "Perfect Style Match",
        "Excellent Theme Match (2 interests)",
        "Perfect Difficulty Level",
        "Ideal Duration",
        "Guaranteed Departure"
      ]
    },
    // ... 9 more trips
  ],
  "message": "Found 10 recommended trips"
}
```

### Error Response (400/500)

```json
{
  "success": false,
  "error": "Error description"
}
```

---

## Example Requests

### Example 1: Cultural Tour in Asia

```bash
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "selected_continents": ["Asia"],
    "preferred_type_id": 1,
    "preferred_theme_ids": [3, 4],
    "min_duration": 10,
    "max_duration": 16,
    "budget": 10000,
    "difficulty": 2,
    "start_date": "2025-02-01"
  }'
```

### Example 2: Budget-Friendly European Adventure

```bash
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "selected_continents": ["Europe"],
    "preferred_type_id": 7,
    "preferred_theme_ids": [7, 4],
    "min_duration": 7,
    "max_duration": 10,
    "budget": 6000,
    "difficulty": 1,
    "start_date": "2025-03-15"
  }'
```

### Example 3: Flexible Search (Minimal Filters)

```bash
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "min_duration": 7,
    "max_duration": 14,
    "budget": 15000,
    "start_date": "2025-01-01"
  }'
```

---

## Integration Notes

### Frontend Integration

```typescript
import { getRecommendations, RecommendationPreferences } from '@/lib/api';

const preferences: RecommendationPreferences = {
  selected_continents: ['Asia'],
  preferred_type_id: 1,      // Geographic Depth
  preferred_theme_ids: [3, 4], // Cultural, Historical
  min_duration: 10,
  max_duration: 16,
  budget: 10000,
  difficulty: 2,
  start_date: '2025-02-01'
};

const response = await getRecommendations(preferences);

if (response.success && response.data) {
  response.data.forEach(trip => {
    console.log(`${trip.title}: ${trip.match_score}/100`);
    console.log(`Reasons: ${trip.match_details.join(', ')}`);
  });
}
```

### Tag Selection

To get TYPE and THEME tags separately:

```typescript
import { getTags } from '@/lib/api';

const tagsResponse = await getTags();
if (tagsResponse.success && tagsResponse.data) {
  const typeTags = tagsResponse.data.filter(t => t.category === 'Type');
  const themeTags = tagsResponse.data.filter(t => t.category === 'Theme');
  
  // Display TYPE tags as radio buttons (single choice)
  // Display THEME tags as checkboxes (multi-select up to 3)
}
```

---

## Scoring Examples

### High Score Example (95/100)

```
User Preferences:
- TYPE: "Safari" ✓
- THEMES: "Wildlife" + "Photography" ✓
- Duration: 7-14 days ✓
- Budget: 15,000 ILS ✓
- Difficulty: 2 ✓

Trip Matches:
- TYPE Match: 25/25 (exact style match)
- THEME Match: 15/15 (2+ themes match)
- Difficulty: 20/20 (exact match)
- Duration: 15/15 (10 days, within range)
- Budget: 15/15 (12,000 ILS, under budget)
- Business: 10/10 (Guaranteed status)
= 100/100 possible

Reasons:
- "Perfect Style Match"
- "Excellent Theme Match (2 interests)"
- "Perfect Difficulty Level"
- "Ideal Duration"
- "Within Budget"
- "Guaranteed Departure"
```

### Medium Score Example (52/100)

```
User Preferences:
- TYPE: "Train Tours"
- THEMES: "Historical" + "Food & Wine"
- Duration: 7-10 days
- Budget: 8,000 ILS
- Difficulty: 1

Trip Matches:
- TYPE Match: 0/25 (trip is "Cruise")
- THEME Match: 7/15 (only "Historical" matches)
- Difficulty: 10/20 (trip is 2, user wants 1)
- Duration: 15/15 (8 days, perfect)
- Budget: 10/15 (8,500 ILS, 106% of budget)
- Business: 10/10 (Last Places)
= 52/100

Reasons:
- "Good Theme Match"
- "Close Difficulty Level"
- "Ideal Duration"
- "Slightly Over Budget"
- "Last Places Available"
```

---

## Testing

Run the test script:

```bash
cd backend
python test_recommendations.py
```

This will test various scenarios and display top recommendations with scores.

---

## Future Enhancements

Potential improvements to the algorithm:

1. **User History**: Weight towards trip types user previously booked
2. **Seasonal Scoring**: Boost trips in optimal seasons
3. **Guide Preferences**: Allow users to request specific guides
4. **Group Size**: Consider user's party size vs. available spots
5. **Multi-Country Tours**: Handle trips spanning multiple countries
6. **Flexible Dates**: Score trips near user's date range
7. **Price Trends**: Consider if price is above/below average for destination

---

**Last Updated**: December 11, 2025  
**API Version**: 1.0

