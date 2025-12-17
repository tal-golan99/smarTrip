"""Check V2 table structure"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text, inspect

insp = inspect(engine)

tables = insp.get_table_names()
print("Database tables:")
for t in sorted(tables):
    print(f"  - {t}")

print("\n")

# Check trip_templates
if 'trip_templates' in tables:
    print("trip_templates columns:")
    for col in insp.get_columns('trip_templates'):
        print(f"  - {col['name']}: {col['type']}")
    
    print(f"\ntrip_templates row count:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM trip_templates"))
        print(f"  {result.scalar()} rows")
else:
    print("trip_templates table does not exist")

print()

# Check trip_occurrences
if 'trip_occurrences' in tables:
    print("trip_occurrences columns:")
    for col in insp.get_columns('trip_occurrences'):
        print(f"  - {col['name']}: {col['type']}")
    
    print(f"\ntrip_occurrences row count:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM trip_occurrences"))
        print(f"  {result.scalar()} rows")
else:
    print("trip_occurrences table does not exist")
