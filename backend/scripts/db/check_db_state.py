"""
Check database state: companies and occurrence distribution
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print('='*60)
    print('DATABASE STATE CHECK')
    print('='*60)
    
    # 1. Check companies assigned to trip_templates
    print('\n[1] COMPANIES ASSIGNED TO TEMPLATES:')
    result = conn.execute(text('''
        SELECT c.name, COUNT(tt.id) as template_count
        FROM companies c
        LEFT JOIN trip_templates tt ON tt.company_id = c.id
        GROUP BY c.id, c.name
        ORDER BY template_count DESC
    ''')).fetchall()
    for r in result:
        print(f'  {r[0]}: {r[1]} templates')
    
    # Check for any templates without company
    no_company = conn.execute(text('''
        SELECT COUNT(*) FROM trip_templates WHERE company_id IS NULL
    ''')).scalar()
    print(f'\n  Templates without company: {no_company}')
    
    # 2. Check if templates have multiple occurrences
    print('\n[2] TEMPLATES WITH MULTIPLE OCCURRENCES:')
    result = conn.execute(text('''
        SELECT tt.id, tt.title, COUNT(o.id) as occurrence_count
        FROM trip_templates tt
        LEFT JOIN trip_occurrences o ON o.trip_template_id = tt.id
        GROUP BY tt.id, tt.title
        ORDER BY occurrence_count DESC
        LIMIT 10
    ''')).fetchall()
    
    for r in result:
        title = r[1][:40] + '...' if len(r[1]) > 40 else r[1]
        print(f'  Template {r[0]}: "{title}" -> {r[2]} occurrence(s)')
    
    # Count distribution
    print('\n[3] OCCURRENCE DISTRIBUTION:')
    result = conn.execute(text('''
        SELECT occurrence_count, COUNT(*) as template_count
        FROM (
            SELECT tt.id, COUNT(o.id) as occurrence_count
            FROM trip_templates tt
            LEFT JOIN trip_occurrences o ON o.trip_template_id = tt.id
            GROUP BY tt.id
        ) sub
        GROUP BY occurrence_count
        ORDER BY occurrence_count
    ''')).fetchall()
    
    for r in result:
        print(f'  {r[0]} occurrence(s): {r[1]} templates')
    
    # Total counts
    print('\n[4] TOTALS:')
    templates = conn.execute(text('SELECT COUNT(*) FROM trip_templates')).scalar()
    occurrences = conn.execute(text('SELECT COUNT(*) FROM trip_occurrences')).scalar()
    print(f'  Total templates: {templates}')
    print(f'  Total occurrences: {occurrences}')
    print(f'  Ratio: {occurrences/templates:.2f} occurrences per template')
