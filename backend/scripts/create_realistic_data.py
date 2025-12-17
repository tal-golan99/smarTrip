"""
Create Realistic Data: Distribute Templates to Companies + Add Multiple Occurrences
===================================================================================

This script:
1. Distributes trip_templates among all 10 companies (varied distribution)
2. Creates additional occurrences for ~30% of templates (repeating trips)
3. Assigns different guides to different occurrences of the same template

This makes the data more realistic - popular trips run multiple times per year
with different guides and dates.
"""

import os
import sys
import random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text


def run():
    print("\n" + "="*70)
    print("CREATE REALISTIC DATA: COMPANIES + MULTIPLE OCCURRENCES")
    print("="*70)
    
    random.seed(42)  # For reproducibility
    
    with engine.connect() as conn:
        try:
            # ============================================
            # STEP 1: GET COMPANIES AND GUIDES
            # ============================================
            print("\n[STEP 1] Loading companies and guides...")
            
            companies = conn.execute(text("SELECT id, name FROM companies ORDER BY id")).fetchall()
            guides = conn.execute(text("SELECT id, name FROM guides ORDER BY id")).fetchall()
            
            print(f"  Found {len(companies)} companies")
            print(f"  Found {len(guides)} guides")
            
            company_ids = [c[0] for c in companies]
            guide_ids = [g[0] for g in guides]
            
            # ============================================
            # STEP 2: REDISTRIBUTE TEMPLATES TO COMPANIES
            # ============================================
            print("\n[STEP 2] Redistributing templates among companies...")
            
            # Get all templates
            templates = conn.execute(text("""
                SELECT id, title, trip_type_id FROM trip_templates ORDER BY id
            """)).fetchall()
            
            print(f"  Found {len(templates)} templates to redistribute")
            
            # Create weighted distribution (some companies are bigger)
            # Company 1: 15%, Company 2: 12%, Company 3: 12%, Companies 4-10: ~8.7% each
            weights = [15, 12, 12, 10, 10, 10, 9, 8, 7, 7]
            
            # Assign templates to companies based on weights
            company_assignments = random.choices(company_ids, weights=weights, k=len(templates))
            
            # Update templates
            for (template_id, title, type_id), new_company_id in zip(templates, company_assignments):
                conn.execute(text("""
                    UPDATE trip_templates SET company_id = :company_id WHERE id = :id
                """), {'company_id': new_company_id, 'id': template_id})
            
            print("  -> Templates redistributed")
            
            # Verify distribution
            dist = conn.execute(text("""
                SELECT c.name, COUNT(tt.id) as count
                FROM companies c
                LEFT JOIN trip_templates tt ON tt.company_id = c.id
                GROUP BY c.id, c.name
                ORDER BY count DESC
            """)).fetchall()
            
            print("\n  New distribution:")
            for name, count in dist:
                print(f"    {name}: {count} templates")
            
            # ============================================
            # STEP 3: CREATE ADDITIONAL OCCURRENCES
            # ============================================
            print("\n[STEP 3] Creating additional occurrences for repeating trips...")
            
            # Select ~30% of templates to have multiple occurrences
            # Popular trips (lower IDs in our seeded data) are more likely to repeat
            templates_for_repeat = []
            for template_id, title, type_id in templates:
                # Higher chance for lower IDs (more established trips)
                repeat_chance = 0.35 - (template_id / 2000)  # 35% to 10%
                if random.random() < repeat_chance:
                    templates_for_repeat.append((template_id, title, type_id))
            
            print(f"  Selected {len(templates_for_repeat)} templates for additional occurrences")
            
            # Get existing occurrence data as reference
            existing_occurrences = conn.execute(text("""
                SELECT o.id, o.trip_template_id, o.start_date, o.end_date, 
                       o.spots_left, o.status, o.guide_id,
                       tt.base_price, tt.default_max_capacity
                FROM trip_occurrences o
                JOIN trip_templates tt ON o.trip_template_id = tt.id
            """)).fetchall()
            
            # Create a lookup for existing occurrences
            template_occurrences = {}
            for occ in existing_occurrences:
                tid = occ[1]
                if tid not in template_occurrences:
                    template_occurrences[tid] = []
                template_occurrences[tid].append(occ)
            
            # Status options
            statuses = ['Open', 'Guaranteed', 'Last Places', 'Full']
            status_weights = [50, 25, 15, 10]
            
            new_occurrences_count = 0
            
            for template_id, title, type_id in templates_for_repeat:
                # Get existing occurrence for this template
                existing = template_occurrences.get(template_id, [])
                if not existing:
                    continue
                
                ref_occ = existing[0]
                ref_start = ref_occ[2]
                ref_end = ref_occ[3]
                base_price = float(ref_occ[7]) if ref_occ[7] else 1000
                max_capacity = ref_occ[8] or 20
                
                # Calculate trip duration
                duration = (ref_end - ref_start).days
                
                # Create 1-3 additional occurrences
                num_additional = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
                
                for i in range(num_additional):
                    # Schedule at different times (spread throughout the year)
                    # Base offset: 2-4 months between occurrences
                    month_offset = (i + 1) * random.randint(60, 120)
                    new_start = ref_start + timedelta(days=month_offset)
                    new_end = new_start + timedelta(days=duration)
                    
                    # Assign a different guide (if possible)
                    available_guides = [g for g in guide_ids if g != ref_occ[6]]
                    new_guide = random.choice(available_guides) if available_guides else ref_occ[6]
                    
                    # Slight price variation (+/- 10%)
                    price_variation = random.uniform(0.9, 1.1)
                    new_price = round(base_price * price_variation, 2)
                    # Only set price_override if different from base
                    price_override = new_price if abs(new_price - base_price) > 10 else None
                    
                    # Random status
                    new_status = random.choices(statuses, weights=status_weights)[0]
                    
                    # Spots left based on status
                    if new_status == 'Full':
                        spots_left = 0
                    elif new_status == 'Last Places':
                        spots_left = random.randint(1, 3)
                    elif new_status == 'Guaranteed':
                        spots_left = random.randint(3, max_capacity // 2)
                    else:  # Open
                        spots_left = random.randint(max_capacity // 2, max_capacity)
                    
                    # Insert new occurrence
                    conn.execute(text("""
                        INSERT INTO trip_occurrences (
                            trip_template_id, guide_id, start_date, end_date,
                            price_override, spots_left, status, created_at, updated_at
                        ) VALUES (
                            :template_id, :guide_id, :start_date, :end_date,
                            :price_override, :spots_left, :status, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """), {
                        'template_id': template_id,
                        'guide_id': new_guide,
                        'start_date': new_start,
                        'end_date': new_end,
                        'price_override': price_override,
                        'spots_left': spots_left,
                        'status': new_status,
                    })
                    
                    new_occurrences_count += 1
            
            print(f"  -> Created {new_occurrences_count} new occurrences")
            
            conn.commit()
            
            # ============================================
            # VERIFICATION
            # ============================================
            print("\n[VERIFICATION]")
            
            # Occurrence distribution
            dist = conn.execute(text("""
                SELECT occurrence_count, COUNT(*) as template_count
                FROM (
                    SELECT tt.id, COUNT(o.id) as occurrence_count
                    FROM trip_templates tt
                    LEFT JOIN trip_occurrences o ON o.trip_template_id = tt.id
                    GROUP BY tt.id
                ) sub
                GROUP BY occurrence_count
                ORDER BY occurrence_count
            """)).fetchall()
            
            print("\n  Occurrence distribution:")
            for occ_count, template_count in dist:
                print(f"    {occ_count} occurrence(s): {template_count} templates")
            
            # Totals
            templates_count = conn.execute(text("SELECT COUNT(*) FROM trip_templates")).scalar()
            occurrences_count = conn.execute(text("SELECT COUNT(*) FROM trip_occurrences")).scalar()
            
            print(f"\n  Total templates: {templates_count}")
            print(f"  Total occurrences: {occurrences_count}")
            print(f"  Ratio: {occurrences_count/templates_count:.2f} occurrences per template")
            
            # Sample multi-occurrence templates
            print("\n  Sample templates with multiple occurrences:")
            samples = conn.execute(text("""
                SELECT tt.title, COUNT(o.id) as occ_count
                FROM trip_templates tt
                JOIN trip_occurrences o ON o.trip_template_id = tt.id
                GROUP BY tt.id, tt.title
                HAVING COUNT(o.id) > 1
                ORDER BY occ_count DESC
                LIMIT 5
            """)).fetchall()
            
            for title, count in samples:
                short_title = title[:45] + '...' if len(title) > 45 else title
                print(f"    \"{short_title}\": {count} departures")
            
            print("\n" + "="*70)
            print("REALISTIC DATA CREATED SUCCESSFULLY")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False


if __name__ == '__main__':
    success = run()
    exit(0 if success else 1)
