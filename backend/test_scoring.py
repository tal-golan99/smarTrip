"""
Recommendation Engine Scoring Analysis
Tests 30 different scenarios to analyze score distribution
"""

from datetime import datetime, timedelta
from app import app, db_session, Trip, Country, TripType, Tag, TripTag, TagCategory, TripStatus
from app import SCORING_WEIGHTS, SCORE_THRESHOLDS, RecommendationConfig

def run_analysis():
    print('='*80)
    print('RECOMMENDATION ENGINE SCORING ANALYSIS')
    print('='*80)

    with app.app_context():
        # Get database stats
        total_trips = db_session.query(Trip).count()
        total_countries = db_session.query(Country).count()
        total_themes = db_session.query(Tag).filter(Tag.category == TagCategory.THEME).count()
        
        print(f'\nDatabase: {total_trips} trips, {total_countries} countries, {total_themes} themes')
        
        print('\n' + '='*80)
        print('CURRENT SCORING WEIGHTS:')
        print('='*80)
        for key, value in SCORING_WEIGHTS.items():
            print(f'  {key}: {value}')
        
        print('\n' + '='*80)
        print('MAXIMUM POSSIBLE SCORE CALCULATION:')
        print('='*80)
        
        base = SCORING_WEIGHTS.get('BASE_SCORE', 0)
        max_theme = SCORING_WEIGHTS['THEME_FULL']
        max_diff = SCORING_WEIGHTS['DIFFICULTY_PERFECT']
        max_dur = SCORING_WEIGHTS['DURATION_IDEAL']
        max_budget = SCORING_WEIGHTS['BUDGET_PERFECT']
        max_status = SCORING_WEIGHTS['STATUS_LAST_PLACES']
        max_soon = SCORING_WEIGHTS['DEPARTING_SOON']
        max_geo = SCORING_WEIGHTS['GEO_DIRECT_COUNTRY']
        
        total_max = base + max_theme + max_diff + max_dur + max_budget + max_status + max_soon + max_geo
        print(f'  BASE SCORE: {base}')
        print(f'  Theme (full match): {max_theme}')
        print(f'  Difficulty (perfect): {max_diff}')
        print(f'  Duration (ideal): {max_dur}')
        print(f'  Budget (perfect): {max_budget}')
        print(f'  Status (last places): {max_status}')
        print(f'  Departing soon: {max_soon}')
        print(f'  Geography (country): {max_geo}')
        print(f'  ----------------------------------------')
        print(f'  TOTAL MAX POSSIBLE: {total_max} (clamped to 100)')
        
        print('\n' + '='*80)
        print('30 SIMULATED SCORING SCENARIOS:')
        print('='*80)
        
        scenarios = []
        
        # Scenario 1-10: Basic combinations (all include base score)
        scenarios.append(('1. Country only', base + max_geo, 'User picks Japan, trip is in Japan'))
        scenarios.append(('2. Country + Duration', base + max_geo + max_dur, 'Country + duration in range'))
        scenarios.append(('3. Country + 1 Theme', base + max_geo + SCORING_WEIGHTS['THEME_PARTIAL'], 'Country + 1 theme match'))
        scenarios.append(('4. Country + 2+ Themes', base + max_geo + max_theme, 'Country + 2+ themes'))
        scenarios.append(('5. Country + Dur + Budget', base + max_geo + max_dur + max_budget, 'Three criteria'))
        scenarios.append(('6. Continent only', base + SCORING_WEIGHTS['GEO_CONTINENT'], 'User picks Asia'))
        scenarios.append(('7. Country + Difficulty', base + max_geo + max_diff, 'Perfect difficulty'))
        scenarios.append(('8. Country + Theme + Dur', base + max_geo + max_theme + max_dur, 'Three criteria'))
        scenarios.append(('9. Country + Budget +10%', base + max_geo + SCORING_WEIGHTS['BUDGET_GOOD'], 'Slightly over'))
        scenarios.append(('10. Full (no status)', base + max_geo + max_theme + max_diff + max_dur + max_budget, 'All but status'))
        
        # Scenario 11-20: Status and urgency
        scenarios.append(('11. Full + Guaranteed', base + max_geo + max_theme + max_diff + max_dur + max_budget + SCORING_WEIGHTS['STATUS_GUARANTEED'], 'With guarantee'))
        scenarios.append(('12. PERFECT SCORE', min(100, base + max_geo + max_theme + max_diff + max_dur + max_budget + max_status + max_soon), 'Everything max (capped)'))
        scenarios.append(('13. Country NO themes', base + max_geo + SCORING_WEIGHTS['THEME_PENALTY'], 'Theme penalty'))
        scenarios.append(('14. Themes only', base + max_theme, 'No location selected'))
        scenarios.append(('15. Country + Dur 4d', base + max_geo + SCORING_WEIGHTS['DURATION_GOOD'], 'Duration close'))
        scenarios.append(('16. Typical search', base + max_geo + SCORING_WEIGHTS['THEME_PARTIAL'] + max_dur, 'Common pattern'))
        scenarios.append(('17. Country + Budget+20%', base + max_geo + SCORING_WEIGHTS['BUDGET_ACCEPTABLE'], 'Over budget'))
        scenarios.append(('18. Country + Dur + Soon', base + max_geo + max_dur + max_soon, 'Leaving soon'))
        scenarios.append(('19. Country + LastPlaces', base + max_geo + max_status, 'Urgency combo'))
        scenarios.append(('20. Duration only', base + max_dur, 'Just duration'))
        
        # Scenario 21-30: Real-world searches
        scenarios.append(('21. Safari search', base + max_geo + SCORING_WEIGHTS['THEME_PARTIAL'] + max_dur + max_budget, 'Africa + Wildlife'))
        scenarios.append(('22. Europe hiking', base + SCORING_WEIGHTS['GEO_CONTINENT'] + max_theme + max_dur + SCORING_WEIGHTS['BUDGET_GOOD'], 'Hiking trip'))
        scenarios.append(('23. Private group', base + max_geo + max_dur + max_theme, 'Flexible duration'))
        scenarios.append(('24. Good but wrong theme', base + max_geo + max_dur + max_budget + SCORING_WEIGHTS['THEME_PENALTY'], 'Penalty applied'))
        scenarios.append(('25. Just urgency', base + max_status + max_soon, 'No user prefs'))
        scenarios.append(('26. Diff close only', base + max_geo + max_dur, 'Close diff no bonus'))
        scenarios.append(('27. Multi-country', base + max_geo + max_theme + max_dur, '3 countries'))
        scenarios.append(('28. Value search', base + max_budget + SCORING_WEIGHTS['STATUS_GUARANTEED'] + max_geo, 'Budget focused'))
        scenarios.append(('29. Interest search', base + max_theme + SCORING_WEIGHTS['DURATION_GOOD'] + max_geo, 'Theme focused'))
        scenarios.append(('30. Realistic avg', base + SCORING_WEIGHTS['GEO_CONTINENT'] + SCORING_WEIGHTS['THEME_PARTIAL'] + SCORING_WEIGHTS['DURATION_GOOD'] + SCORING_WEIGHTS['BUDGET_GOOD'], 'Average match'))
        
        # Print all scenarios
        print(f'\n{"#":<25} {"Score":>6} {"Color":>10}  {"Description"}')
        print('-'*75)
        
        low_scores = 0
        mid_scores = 0
        high_scores = 0
        
        for name, score, desc in scenarios:
            if score >= SCORE_THRESHOLDS['HIGH']:
                color = 'TURQUOISE'
                high_scores += 1
            elif score >= SCORE_THRESHOLDS['MID']:
                color = 'ORANGE'
                mid_scores += 1
            else:
                color = 'RED'
                low_scores += 1
            print(f'{name:<25} {score:>6.0f} {color:>10}  {desc}')
        
        print('\n' + '='*80)
        print('SCORE DISTRIBUTION:')
        print('='*80)
        print(f'  HIGH (Turquoise, >=70): {high_scores}/30 ({high_scores/30*100:.0f}%)')
        print(f'  MID (Orange, 50-69):    {mid_scores}/30 ({mid_scores/30*100:.0f}%)')
        print(f'  LOW (Red, <50):         {low_scores}/30 ({low_scores/30*100:.0f}%)')
        
        print('\n' + '='*80)
        print('PROBLEM ANALYSIS:')
        print('='*80)
        
        # Identify problematic scenarios
        problems = []
        for name, score, desc in scenarios:
            # Good matches that are scoring low
            if 'Country +' in name and score < 50:
                problems.append((name, score, 'Country match should be at least ORANGE'))
            if 'Typical' in name and score < 60:
                problems.append((name, score, 'Typical search should score higher'))
            if 'Safari' in name or 'hiking' in name.lower():
                if score < 60:
                    problems.append((name, score, 'Real-world search should score higher'))
        
        if problems:
            print('\nProblematic scenarios (good matches with low scores):')
            for name, score, issue in problems:
                print(f'  - {name}: {score:.0f} - {issue}')
        
        print('\n' + '='*80)
        print('RECOMMENDATIONS:')
        print('='*80)
        
        # Calculate what percentage of scenarios get good scores
        good_score_pct = (high_scores + mid_scores) / 30 * 100
        
        print(f'''
ISSUES IDENTIFIED:
1. Base score is 0, so trips start with nothing
2. Many reasonable matches score below 50 (RED)
3. Country-only match (15 pts) = RED
4. Realistic average user gets only {scenarios[29][1]:.0f} points = {"RED" if scenarios[29][1] < 50 else "ORANGE" if scenarios[29][1] < 70 else "TURQUOISE"}

SUGGESTED FIXES:

Option A: Add Base Score
  - Give all trips a base score of 30-40 points
  - This means "passing" hard filters already counts for something
  - Current: Trip passes filters = 0 points
  - Fixed: Trip passes filters = 35 points base

Option B: Increase Individual Weights
  - GEO_DIRECT_COUNTRY: 15 -> 25 (country match is important!)
  - THEME_FULL: 25 -> 30
  - DURATION_IDEAL: 12 -> 18
  - BUDGET_PERFECT: 12 -> 18

Option C: Lower Thresholds
  - HIGH: 70 -> 55
  - MID: 50 -> 35
  - This makes scores relative to current weights

RECOMMENDED: Option A (Base Score of 35)
  - Simple fix
  - Rewards trips for passing hard filters
  - Current avg score: ~{sum(s[1] for s in scenarios)/30:.0f}
  - With base 35: ~{sum(s[1] for s in scenarios)/30 + 35:.0f}

Alternatively: Combine Base Score (25) + Increase key weights:
  - BASE_SCORE: 25
  - GEO_DIRECT_COUNTRY: 15 -> 20
  - DURATION_IDEAL: 12 -> 15
  - BUDGET_PERFECT: 12 -> 15
''')

if __name__ == '__main__':
    run_analysis()

