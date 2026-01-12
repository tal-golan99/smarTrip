"""
Recommendation Engine Scoring Analysis v2
Comprehensive analysis with actionable insights

Run from backend folder: python scripts/analyze_scoring_v2.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app import app, db_session, Trip, Country, TripType, Tag, TripStatus
# Note: TagCategory enum was removed
from app.services.recommendation import SCORING_WEIGHTS, SCORE_THRESHOLDS, RecommendationConfig

def run_analysis():
    print('='*80)
    print('RECOMMENDATION ENGINE SCORING ANALYSIS v2')
    print('='*80)

    with app.app_context():
        # Current weights
        base = SCORING_WEIGHTS.get('BASE_SCORE', 0)
        max_theme = SCORING_WEIGHTS['THEME_FULL']
        max_diff = SCORING_WEIGHTS['DIFFICULTY_PERFECT']
        max_dur = SCORING_WEIGHTS['DURATION_IDEAL']
        max_budget = SCORING_WEIGHTS['BUDGET_PERFECT']
        max_status = SCORING_WEIGHTS['STATUS_LAST_PLACES']
        max_soon = SCORING_WEIGHTS['DEPARTING_SOON']
        max_geo = SCORING_WEIGHTS['GEO_DIRECT_COUNTRY']
        theme_penalty = SCORING_WEIGHTS['THEME_PENALTY']
        
        # Calculate theoretical max
        theoretical_max = base + max_theme + max_diff + max_dur + max_budget + max_status + max_soon + max_geo
        
        print(f'\n{"="*80}')
        print('QUESTION 1: Does BASE_SCORE change the max of 100?')
        print('='*80)
        print(f'''
Current Configuration:
  BASE_SCORE: {base}
  All bonuses: {max_theme + max_diff + max_dur + max_budget + max_status + max_soon + max_geo}
  
Theoretical Maximum: {theoretical_max}
Actual Maximum: 100 (clamped in code)

ANSWER: YES, technically the sum exceeds 100, but the code clamps it:
  final_score = max(0.0, min(100.0, current_score))

This means a "perfect" trip will show as 100, not {theoretical_max:.0f}.
This is GOOD - it keeps scores on a clean 0-100 scale.
''')

        print('='*80)
        print('QUESTION 2: Score Distribution Analysis')
        print('='*80)
        
        # Generate all 30 scenarios
        scenarios = []
        
        # User effort levels
        scenarios.append(('Minimal: Continent only', base + SCORING_WEIGHTS['GEO_CONTINENT'], 'Picked just a continent'))
        scenarios.append(('Minimal: Duration only', base + max_dur, 'Only duration specified'))
        scenarios.append(('Low: Country only', base + max_geo, 'Picked one country'))
        scenarios.append(('Low: Country + Dur', base + max_geo + max_dur, 'Country and duration'))
        scenarios.append(('Medium: Country+1Theme+Dur', base + max_geo + SCORING_WEIGHTS['THEME_PARTIAL'] + max_dur, 'Common pattern'))
        scenarios.append(('Medium: Country+Budget+Dur', base + max_geo + max_budget + max_dur, 'Budget focused'))
        scenarios.append(('High: Country+2Themes+Dur', base + max_geo + max_theme + max_dur, 'Interest focused'))
        scenarios.append(('High: Full criteria', base + max_geo + max_theme + max_diff + max_dur + max_budget, 'All filled'))
        scenarios.append(('Perfect: Everything+Status', min(100, theoretical_max), 'Perfect match'))
        
        # Penalty scenarios
        scenarios.append(('Penalty: Wrong themes', base + max_geo + max_dur + theme_penalty, 'Has theme penalty'))
        
        print(f'\n{"User Effort Level":<30} {"Score":>6} {"Color":>10}')
        print('-'*50)
        
        for name, score, _ in scenarios:
            if score >= SCORE_THRESHOLDS['HIGH']:
                color = 'TURQUOISE'
            elif score >= SCORE_THRESHOLDS['MID']:
                color = 'ORANGE'
            else:
                color = 'RED'
            print(f'{name:<30} {score:>6.0f} {color:>10}')

        print(f'\n{"="*80}')
        print('QUESTION 3: Does showing message for ORANGE+RED make sense?')
        print('='*80)
        
        # Analyze when message appears
        message_scenarios = [
            ('Country only', base + max_geo, 'ORANGE'),
            ('Country + Duration', base + max_geo + max_dur, 'ORANGE'),
            ('Continent only', base + SCORING_WEIGHTS['GEO_CONTINENT'], 'RED'),
            ('Duration only', base + max_dur, 'RED'),
            ('Country + 1 Theme + Dur', base + max_geo + SCORING_WEIGHTS['THEME_PARTIAL'] + max_dur, 'TURQUOISE (74)'),
        ]
        
        print('''
Current Logic: Show refinement message when top_score < 70 (TURQUOISE threshold)

Analysis of common searches:
''')
        for name, score, note in message_scenarios:
            shows_msg = score < SCORE_THRESHOLDS['HIGH']
            print(f'  {name}: {score:.0f} -> {"SHOWS MESSAGE" if shows_msg else "No message"} ({note})')
        
        print('''
VERDICT: The current logic makes sense!

- RED scores (< 50): User gave minimal input, DEFINITELY should refine
- ORANGE scores (50-69): Partial match, COULD benefit from more criteria
- TURQUOISE (>= 70): Good match, no message needed

HOWEVER, consider this edge case:
- "Country + Duration" = 62 (ORANGE) -> Shows message
- Is this really a "bad" match? The user picked a country and duration!

SUGGESTION: You might want to:
Option A: Keep current (conservative - always encourage more filters)
Option B: Only show for RED (< 50) - user gave very little input
Option C: Lower threshold to 60 - middle ground
''')

        print('='*80)
        print('QUESTION 4: Are current weights balanced?')
        print('='*80)
        
        print('''
Weight Analysis (relative importance):
''')
        weights_sorted = [
            ('BASE_SCORE', base, 'Foundation for passing filters'),
            ('THEME_FULL', max_theme, 'User interests match (2+)'),
            ('GEO_DIRECT_COUNTRY', max_geo, 'Exact country match'),
            ('DIFFICULTY_PERFECT', max_diff, 'Activity level match'),
            ('STATUS_LAST_PLACES', max_status, 'Urgency - selling fast'),
            ('DURATION_IDEAL', max_dur, 'Trip length match'),
            ('BUDGET_PERFECT', max_budget, 'Price match'),
            ('THEME_PARTIAL', SCORING_WEIGHTS['THEME_PARTIAL'], 'Partial theme (1)'),
            ('DURATION_GOOD', SCORING_WEIGHTS['DURATION_GOOD'], 'Close duration'),
            ('BUDGET_GOOD', SCORING_WEIGHTS['BUDGET_GOOD'], 'Close budget'),
            ('STATUS_GUARANTEED', SCORING_WEIGHTS['STATUS_GUARANTEED'], 'Confirmed departure'),
            ('DEPARTING_SOON', max_soon, 'Leaving within 30 days'),
            ('GEO_CONTINENT', SCORING_WEIGHTS['GEO_CONTINENT'], 'Continent match'),
            ('BUDGET_ACCEPTABLE', SCORING_WEIGHTS['BUDGET_ACCEPTABLE'], 'Over budget 20%'),
        ]
        
        for name, weight, desc in sorted(weights_sorted, key=lambda x: -x[1]):
            bar = '*' * int(weight / 2)
            print(f'  {name:<22} {weight:>5.0f}  {bar:<20} {desc}')
        
        print(f'''
Total available points: {sum(w[1] for w in weights_sorted):.0f}
(But capped at 100)
''')

        print('='*80)
        print('RECOMMENDATIONS')
        print('='*80)
        
        print('''
CURRENT STATE: GOOD!
The scoring distribution is now healthy after adding BASE_SCORE = 35.

POTENTIAL TWEAKS TO CONSIDER:

1. REFINEMENT MESSAGE THRESHOLD
   Current: Shows for score < 70 (orange + red)
   
   Option A (Current): Keep at < 70
   - Pro: Encourages users to add more filters
   - Con: "Country + Duration" shows message (might annoy users)
   
   Option B: Change to < 50 (red only)
   - Pro: Only shows when user gave minimal input
   - Con: Misses partial matches that could improve
   
   RECOMMENDED: Keep current (< 70) - it's helpful, not annoying

2. THEME_PENALTY might be too harsh?
   Current: -15 points
   With base 35, a trip with theme penalty = 35 + 15 - 15 = 35 (RED)
   
   Option: Reduce to -10
   Result: 35 + 15 - 10 = 40 (still RED, but less harsh)
   
   RECOMMENDED: Keep at -15 - it correctly penalizes mismatches

3. CONTINENT vs COUNTRY gap
   Country match: +15
   Continent match: +5
   Gap: 10 points
   
   This means selecting a specific country is 3x more valuable.
   RECOMMENDED: This is correct - specific > general

4. Should BASE_SCORE be visible to user?
   Currently: Shows in match_details as "Base Score [+35]"
   
   Option: Hide it from match_details (it's implicit)
   RECOMMENDED: Hide it - users don't need to see it

FINAL VERDICT: System is well-calibrated! Only minor tweak suggested:
- Consider hiding "Base Score [+35]" from match_details
''')

        # Count actual database scenarios
        print('='*80)
        print('REAL DATABASE CHECK')
        print('='*80)
        
        # Check how many trips have themes
        trips_with_themes = db_session.query(Trip).join(Trip.trip_tags).distinct().count()
        total_trips = db_session.query(Trip).count()
        
        print(f'''
Database Statistics:
  Total trips: {total_trips}
  Trips with theme tags: {trips_with_themes} ({trips_with_themes/total_trips*100:.0f}%)
  Trips without themes: {total_trips - trips_with_themes}
  
If many trips lack themes, the THEME_PENALTY will frequently apply!
''')

if __name__ == '__main__':
    run_analysis()

