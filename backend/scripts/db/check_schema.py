"""Check database schema for tags table"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'tags' ORDER BY ordinal_position
    """))
    print('Tags table columns:')
    for row in result:
        print(f'  - {row[0]}')
